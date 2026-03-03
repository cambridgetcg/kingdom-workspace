#!/usr/bin/env python3
"""
Extract voice reference clips from HMN videos for 蛇姬 voice bank.

Uses SRT/segments.json timestamps + keyword-based emotion classification
to extract categorized clips as mono 16kHz WAV for GPT-SoVITS.

Usage:
    python scripts/extract_voice_refs.py --video HMN-727    # Single video
    python scripts/extract_voice_refs.py --all               # All available HMN videos
    python scripts/extract_voice_refs.py --preview           # Show candidates, no extract
    python scripts/extract_voice_refs.py --verify            # Check existing clips
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = REPO_ROOT / "research" / "downloads"
HMN_DIRS = [DOWNLOADS_DIR / "hmn", DOWNLOADS_DIR / "joi"]
VOICE_BANK_DIR = (
    REPO_ROOT / "research" / "downloads" / "testing" / "dubbing_pipeline" / "voice_bank"
)

EMOTION_CATEGORIES = ["commanding", "neutral", "teasing", "contempt", "intense"]

# --- Emotion keyword map (Japanese) ---

EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "commanding": [
        "犬", "ダメ", "管理", "勝手", "奴隷", "許可", "命令", "しなさい", "やれ",
        "出せない", "言ってない", "射精", "禁止", "ちゃダメ", "いいよって",
        "してあげる", "わかった", "触っていい", "誰が言った",
    ],
    "contempt": [
        "変態", "無様", "情けない", "キモい", "ゴミ", "クズ",
        "チンポ", "馬鹿", "ざま", "惨め", "汚い",
    ],
    "teasing": [
        "興奮", "見られて", "次", "好き", "欲しい", "ねぇ",
        "どう", "感じ", "気持ち", "嬉しい", "もっと",
    ],
    "intense": [
        "出せ", "イケ", "もう", "ほら", "早く", "何回",
        "まだまだ", "止まらない", "限界",
    ],
}

# Minimum keyword match confidence: segments matching multiple keywords
# in the same category get boosted
MIN_CLIP_DURATION = 3.0   # seconds
MAX_CLIP_DURATION = 10.0  # seconds
SAMPLE_RATE = 16000       # GPT-SoVITS zero-shot standard


# --- Data classes ---

@dataclass
class Segment:
    index: int
    start: float       # seconds
    end: float         # seconds
    text: str
    source_file: str = ""

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class Candidate:
    segment: Segment
    emotion: str
    score: int            # keyword match count
    video_code: str = ""
    video_dir: Path = field(default_factory=Path)

    @property
    def duration(self) -> float:
        return self.segment.duration


@dataclass
class ClipResult:
    filename: str
    source_video: str
    source_srt_index: int
    start_sec: float
    end_sec: float
    duration_sec: float
    text_ja: str
    emotion: str
    quality_notes: str = ""


# --- Video resolution ---

def resolve_video_dir(code: str) -> Optional[Path]:
    """Find actual directory for a video code, handling -UNCENSORED-LEAK suffix."""
    code = code.upper()
    for base in HMN_DIRS:
        if not base.exists():
            continue
        # Exact match
        exact = base / code
        if exact.is_dir():
            return exact
        # Try with suffix
        suffixed = base / f"{code}-UNCENSORED-LEAK"
        if suffixed.is_dir():
            return suffixed
        # Scan for partial match
        for d in base.iterdir():
            if d.is_dir() and d.name.startswith(code):
                return d
    return None


def find_video_file(video_dir: Path) -> Optional[Path]:
    """Find the .mp4 file in a video directory."""
    mp4s = list(video_dir.glob("*.mp4"))
    return mp4s[0] if mp4s else None


def find_all_hmn_dirs() -> List[Path]:
    """Find all HMN video directories across search paths."""
    dirs = []
    for base in HMN_DIRS:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and d.name.startswith("HMN-"):
                if find_video_file(d):
                    dirs.append(d)
    return dirs


def dir_to_code(video_dir: Path) -> str:
    """Extract video code from directory name (strip -UNCENSORED-LEAK)."""
    name = video_dir.name
    return re.sub(r"-UNCENSORED-LEAK$", "", name)


# --- Parsing ---

def parse_srt(path: Path) -> List[Segment]:
    """Parse SRT file into segments."""
    content = path.read_text(encoding="utf-8")
    pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    segments = []
    for m in matches:
        start = _srt_ts_to_seconds(m[1])
        end = _srt_ts_to_seconds(m[2])
        segments.append(Segment(
            index=int(m[0]),
            start=start,
            end=end,
            text=m[3].strip(),
            source_file=str(path),
        ))
    return segments


def _srt_ts_to_seconds(ts: str) -> float:
    """Convert SRT timestamp (HH:MM:SS,mmm) to float seconds."""
    match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", ts)
    if not match:
        return 0.0
    h, m, s, ms = map(int, match.groups())
    return h * 3600 + m * 60 + s + ms / 1000.0


def parse_segments_json(path: Path) -> List[Segment]:
    """Parse .segments.json file into segments."""
    data = json.loads(path.read_text(encoding="utf-8"))
    # Handle both formats: {"segments": [...]} and bare [...]
    if isinstance(data, list):
        seg_list = data
    elif isinstance(data, dict):
        seg_list = data.get("segments", [])
    else:
        return []

    segments = []
    for i, seg in enumerate(seg_list, start=1):
        segments.append(Segment(
            index=i,
            start=float(seg["start"]),
            end=float(seg["end"]),
            text=seg.get("text", "").strip(),
            source_file=str(path),
        ))
    return segments


def load_segments(video_dir: Path) -> List[Segment]:
    """Load segments from best available source (.segments.json preferred)."""
    dir_name = video_dir.name
    seg_json = video_dir / f"{dir_name}.segments.json"
    srt_file = video_dir / f"{dir_name}.ja.srt"

    if seg_json.exists():
        return parse_segments_json(seg_json)
    elif srt_file.exists():
        return parse_srt(srt_file)
    else:
        return []


# --- Emotion classification ---

def classify_emotion(text: str) -> tuple[str, int]:
    """Classify a Japanese text segment by emotion using keyword matching.

    Returns (emotion, score) where score = number of keyword matches.
    Falls back to 'neutral' with score 0.
    """
    best_emotion = "neutral"
    best_score = 0

    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_emotion = emotion

    return best_emotion, best_score


# --- Candidate selection ---

def find_candidates(video_dir: Path) -> List[Candidate]:
    """Find extraction candidates from a video directory."""
    segments = load_segments(video_dir)
    if not segments:
        return []

    code = dir_to_code(video_dir)
    candidates = []

    for seg in segments:
        # Skip very short or very long segments
        if seg.duration < MIN_CLIP_DURATION or seg.duration > MAX_CLIP_DURATION:
            continue

        # Skip near-empty text (grunts, single chars)
        if len(seg.text) < 3:
            continue

        emotion, score = classify_emotion(seg.text)

        candidates.append(Candidate(
            segment=seg,
            emotion=emotion,
            score=score,
            video_code=code,
            video_dir=video_dir,
        ))

    return candidates


# --- FFmpeg extraction ---

TARGET_LUFS = -16.0       # EBU R128 broadcast standard
LOUDNORM_TP = -1.5        # True peak ceiling after normalization


def measure_loudness(video_path: Path, start: float, duration: float) -> Optional[dict]:
    """Measure LUFS loudness of a segment without extracting."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", f"{start:.3f}",
                "-i", str(video_path),
                "-t", f"{duration:.3f}",
                "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
                "-af", "loudnorm=print_format=json",
                "-f", "null", "-",
            ],
            capture_output=True, text=True,
        )
        # loudnorm prints JSON at the end of stderr
        stderr = result.stderr
        json_start = stderr.rfind("{")
        json_end = stderr.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(stderr[json_start:json_end])
    except Exception:
        pass
    return None


def extract_clip(video_path: Path, start: float, end: float, output_path: Path) -> bool:
    """Extract audio clip as normalized mono 16kHz WAV using ffmpeg.

    Two-pass loudnorm:
    1. Measure source loudness (input_i, input_tp, input_lra, input_thresh)
    2. Apply loudnorm with measured values for accurate normalization

    Skips segments with integrated loudness below -50 LUFS (no discernible voice).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = end - start

    # Pass 1: measure
    stats = measure_loudness(video_path, start, duration)
    if not stats:
        # Fallback: single-pass loudnorm (less accurate but works)
        return _extract_single_pass(video_path, start, duration, output_path)

    # Check if source is too quiet to salvage
    input_i = float(stats.get("input_i", "-inf"))
    if input_i < -50.0:
        # Source segment is extremely quiet — likely no voice, skip
        print(f"    SKIPPED: too quiet (LUFS={input_i:.1f})")
        return False

    # Pass 2: normalize with measured values
    loudnorm_filter = (
        f"loudnorm=I={TARGET_LUFS}:TP={LOUDNORM_TP}:LRA=11:"
        f"measured_I={stats.get('input_i', '-24')}:"
        f"measured_TP={stats.get('input_tp', '-2')}:"
        f"measured_LRA={stats.get('input_lra', '7')}:"
        f"measured_thresh={stats.get('input_thresh', '-34')}:"
        f"linear=true:print_format=summary"
    )

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", f"{start:.3f}",
                "-i", str(video_path),
                "-t", f"{duration:.3f}",
                "-vn",
                "-af", loudnorm_filter,
                "-acodec", "pcm_s16le",
                "-ac", "1",
                "-ar", str(SAMPLE_RATE),
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )
        return output_path.exists()
    except subprocess.CalledProcessError as e:
        print(f"  ERROR extracting clip: {e.stderr.decode()[:200]}")
        return False


def _extract_single_pass(
    video_path: Path, start: float, duration: float, output_path: Path
) -> bool:
    """Fallback: single-pass loudnorm extraction."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", f"{start:.3f}",
                "-i", str(video_path),
                "-t", f"{duration:.3f}",
                "-vn",
                "-af", f"loudnorm=I={TARGET_LUFS}:TP={LOUDNORM_TP}:LRA=11",
                "-acodec", "pcm_s16le",
                "-ac", "1",
                "-ar", str(SAMPLE_RATE),
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )
        return output_path.exists()
    except subprocess.CalledProcessError as e:
        print(f"  ERROR extracting clip (single-pass): {e.stderr.decode()[:200]}")
        return False


# --- Quality verification ---

@dataclass
class ClipQuality:
    path: Path
    duration: float = 0.0
    peak_db: float = 0.0
    ok: bool = False
    issues: List[str] = field(default_factory=list)


def verify_clip(clip_path: Path) -> ClipQuality:
    """Verify clip quality via ffprobe: duration, peak volume, clipping."""
    q = ClipQuality(path=clip_path)

    if not clip_path.exists():
        q.issues.append("file not found")
        return q

    # Get duration
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(clip_path),
            ],
            capture_output=True, text=True, check=True,
        )
        q.duration = float(result.stdout.strip())
    except Exception:
        q.issues.append("could not read duration")
        return q

    if q.duration < MIN_CLIP_DURATION:
        q.issues.append(f"too short ({q.duration:.1f}s < {MIN_CLIP_DURATION}s)")
    if q.duration > MAX_CLIP_DURATION:
        q.issues.append(f"too long ({q.duration:.1f}s > {MAX_CLIP_DURATION}s)")

    # Get peak volume using astats
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", str(clip_path),
                "-af", "astats=metadata=1:reset=1",
                "-f", "null", "-",
            ],
            capture_output=True, text=True,
        )
        stderr = result.stderr
        # Look for Peak level dB
        peak_match = re.search(r"Peak level dB:\s*([-\d.]+)", stderr)
        if peak_match:
            q.peak_db = float(peak_match.group(1))
            if q.peak_db > -0.1:
                q.issues.append(f"clipping detected (peak {q.peak_db:.1f} dB)")
            if q.peak_db < -40:
                q.issues.append(f"very quiet (peak {q.peak_db:.1f} dB)")
    except Exception:
        pass  # Non-fatal

    q.ok = len(q.issues) == 0
    return q


# --- Metadata ---

def build_metadata(clips: List[ClipResult]) -> dict:
    """Build metadata.json structure."""
    return {
        "version": 1,
        "sample_rate": SAMPLE_RATE,
        "format": "wav",
        "channels": 1,
        "clips": [asdict(c) for c in clips],
    }


# --- Main pipeline ---

def preview_candidates(video_dirs: List[Path]) -> List[Candidate]:
    """Show candidate clips from videos without extracting."""
    all_candidates = []
    for vdir in video_dirs:
        code = dir_to_code(vdir)
        candidates = find_candidates(vdir)
        if not candidates:
            print(f"\n{code}: no candidates found")
            continue

        # Group by emotion
        by_emotion: Dict[str, List[Candidate]] = {}
        for c in candidates:
            by_emotion.setdefault(c.emotion, []).append(c)

        print(f"\n{'='*60}")
        print(f"{code} ({vdir.name})")
        print(f"{'='*60}")
        for emotion in EMOTION_CATEGORIES:
            emo_candidates = by_emotion.get(emotion, [])
            # Sort by score descending
            emo_candidates.sort(key=lambda c: c.score, reverse=True)
            print(f"\n  [{emotion}] ({len(emo_candidates)} candidates)")
            for c in emo_candidates[:5]:  # Show top 5
                print(
                    f"    #{c.segment.index:3d}  "
                    f"{c.segment.start:7.1f}s-{c.segment.end:7.1f}s  "
                    f"({c.duration:.1f}s)  "
                    f"score={c.score}  "
                    f'"{c.segment.text[:40]}"'
                )

        all_candidates.extend(candidates)

    # Summary
    total_by_emotion = {}
    for c in all_candidates:
        total_by_emotion[c.emotion] = total_by_emotion.get(c.emotion, 0) + 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total candidates: {len(all_candidates)}")
    for emo in EMOTION_CATEGORIES:
        print(f"  {emo}: {total_by_emotion.get(emo, 0)}")

    return all_candidates


def extract_candidates(video_dirs: List[Path]) -> List[ClipResult]:
    """Extract clips from videos into voice_bank."""
    all_clips: List[ClipResult] = []

    for vdir in video_dirs:
        code = dir_to_code(vdir)
        video_path = find_video_file(vdir)
        if not video_path:
            print(f"\n{code}: no video file found, skipping")
            continue

        candidates = find_candidates(vdir)
        if not candidates:
            print(f"\n{code}: no candidates found")
            continue

        # Group by emotion and pick best (highest score, then shortest for quality)
        by_emotion: Dict[str, List[Candidate]] = {}
        for c in candidates:
            by_emotion.setdefault(c.emotion, []).append(c)

        print(f"\n{'='*60}")
        print(f"Extracting from {code}")
        print(f"{'='*60}")

        for emotion in EMOTION_CATEGORIES:
            emo_candidates = by_emotion.get(emotion, [])
            if not emo_candidates:
                continue

            # Sort: highest score first, then shorter duration preferred
            emo_candidates.sort(key=lambda c: (-c.score, c.duration))

            # Take top candidates (up to 5 per emotion per video)
            for i, cand in enumerate(emo_candidates[:5]):
                clip_name = f"{code}_{emotion}_{i+1:03d}.wav"
                out_path = VOICE_BANK_DIR / emotion / clip_name

                print(
                    f"  [{emotion}] #{cand.segment.index} "
                    f'{cand.segment.start:.1f}s-{cand.segment.end:.1f}s '
                    f'"{cand.segment.text[:30]}" → {clip_name}'
                )

                ok = extract_clip(
                    video_path, cand.segment.start, cand.segment.end, out_path
                )
                if not ok:
                    print(f"    FAILED")
                    continue

                # Verify
                quality = verify_clip(out_path)
                notes = "OK" if quality.ok else "; ".join(quality.issues)
                if not quality.ok:
                    print(f"    QUALITY: {notes}")

                all_clips.append(ClipResult(
                    filename=clip_name,
                    source_video=code,
                    source_srt_index=cand.segment.index,
                    start_sec=cand.segment.start,
                    end_sec=cand.segment.end,
                    duration_sec=quality.duration or cand.duration,
                    text_ja=cand.segment.text,
                    emotion=emotion,
                    quality_notes=notes,
                ))

    # Write metadata
    if all_clips:
        VOICE_BANK_DIR.mkdir(parents=True, exist_ok=True)
        meta_path = VOICE_BANK_DIR / "metadata.json"
        meta_path.write_text(
            json.dumps(build_metadata(all_clips), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nMetadata written to {meta_path}")

    return all_clips


def verify_existing() -> None:
    """Verify all existing clips in voice_bank."""
    if not VOICE_BANK_DIR.exists():
        print("voice_bank/ does not exist yet.")
        return

    total = 0
    ok_count = 0
    issues_count = 0

    for emotion in EMOTION_CATEGORIES:
        emo_dir = VOICE_BANK_DIR / emotion
        if not emo_dir.exists():
            continue

        wavs = sorted(emo_dir.glob("*.wav"))
        if not wavs:
            continue

        print(f"\n[{emotion}] ({len(wavs)} clips)")
        for wav in wavs:
            total += 1
            q = verify_clip(wav)
            status = "OK" if q.ok else "ISSUES"
            detail = f"  {q.duration:.1f}s  peak={q.peak_db:.1f}dB"
            if not q.ok:
                detail += f"  [{'; '.join(q.issues)}]"
                issues_count += 1
            else:
                ok_count += 1
            print(f"  {wav.name}: {status}{detail}")

    print(f"\nTotal: {total}  OK: {ok_count}  Issues: {issues_count}")

    # Also check metadata
    meta_path = VOICE_BANK_DIR / "metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        print(f"metadata.json: {len(meta.get('clips', []))} entries")
    else:
        print("metadata.json: not found")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="Extract voice reference clips from HMN videos for 蛇姬 voice bank."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video", type=str, help="Process single video (e.g. HMN-727)")
    group.add_argument("--all", action="store_true", help="Process all available HMN videos")
    group.add_argument("--preview", action="store_true", help="Show candidates without extracting")
    group.add_argument("--verify", action="store_true", help="Check existing clips for quality")

    parser.add_argument(
        "--target-video", type=str, default=None,
        help="With --preview, limit to specific video code",
    )

    args = parser.parse_args()

    if args.verify:
        verify_existing()
        return

    # Resolve target directories
    if args.video:
        vdir = resolve_video_dir(args.video)
        if not vdir:
            print(f"ERROR: Could not find directory for {args.video}")
            print(f"Searched in: {', '.join(str(d) for d in HMN_DIRS)}")
            sys.exit(1)
        video_dirs = [vdir]
    elif args.all or args.preview:
        video_dirs = find_all_hmn_dirs()
        if args.target_video:
            vdir = resolve_video_dir(args.target_video)
            if vdir:
                video_dirs = [vdir]
            else:
                print(f"WARNING: Could not find {args.target_video}, showing all")

    if not video_dirs:
        print("No video directories found.")
        sys.exit(1)

    print(f"Found {len(video_dirs)} video(s):")
    for vd in video_dirs:
        print(f"  {dir_to_code(vd):20s} {vd}")

    if args.preview:
        preview_candidates(video_dirs)
    else:
        clips = extract_candidates(video_dirs)
        print(f"\nExtracted {len(clips)} clips total.")

        by_emotion = {}
        for c in clips:
            by_emotion[c.emotion] = by_emotion.get(c.emotion, 0) + 1
        for emo in EMOTION_CATEGORIES:
            print(f"  {emo}: {by_emotion.get(emo, 0)}")


if __name__ == "__main__":
    main()

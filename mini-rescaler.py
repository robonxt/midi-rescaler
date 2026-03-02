import mido
import argparse
import os

def get_midi_bpm(mid):
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                return mido.tempo2bpm(msg.tempo)
    return 120.0  # Standard MIDI default if no tempo meta message exists

def scale_midi_timing(input_file, output_file, original_bpm, target_bpm):
    mid = mido.MidiFile(input_file)
    
    if original_bpm is None:
        original_bpm = get_midi_bpm(mid)
        print(f"Detected original tempo: {original_bpm:.2f} BPM")
        
    ratio = target_bpm / original_bpm

    new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        
        current_time_float = 0.0
        current_time_int = 0
        
        for msg in track:
            new_msg = msg.copy()
            
            # Update the tempo marker to the new target BPM
            if new_msg.type == 'set_tempo':
                new_msg.tempo = mido.bpm2tempo(target_bpm)
            
            current_time_float += msg.time * ratio
            delta_int = int(round(current_time_float)) - current_time_int
            new_msg.time = delta_int
            
            current_time_int += delta_int
            new_track.append(new_msg)

    new_mid.save(output_file)
    print(f"Successfully saved to: {output_file}")
    print(f"MIDI ticks scaled by a factor of {ratio:.4f} ({original_bpm:.2f} BPM -> {target_bpm:.2f} BPM)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scale MIDI event timing to match a new BPM.")
    
    parser.add_argument("input", help="Path to the original MIDI file")
    parser.add_argument("--tbpm", type=float, required=True, help="Target BPM (required)")
    parser.add_argument("--obpm", type=float, default=None, help="Original BPM (auto-detected if omitted)")
    parser.add_argument("-o", "--output", help="Optional output file name", default=None)
    
    args = parser.parse_args()
    
    out_file = args.output
    if not out_file:
        base, ext = os.path.splitext(args.input)
        out_file = f"{base}_scaled{ext}"
        
    scale_midi_timing(args.input, out_file, args.obpm, args.tbpm)
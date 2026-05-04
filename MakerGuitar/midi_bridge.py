import serial
import mido

# --- MAC CONFIGURATION ---
# Replace this with your exact port from the Arduino IDE (e.g., '/dev/cu.usbmodem14101')
SERIAL_PORT = '/dev/cu.usbmodem14101' 
BAUD_RATE = 115200

# The default name for the Mac IAC Driver port
MIDI_PORT_NAME = 'IAC Driver Bus 1' 

def main():
    print("Available MIDI Outputs:")
    for name in mido.get_output_names():
        print(f" - {name}")
    print("-" * 20)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print(f"Listening to Makerboard on {SERIAL_PORT}...")

        # We look for the IAC Driver port name
        target_port = next((port for port in mido.get_output_names() if MIDI_PORT_NAME in port), None)
        
        if not target_port:
             print(f"Error: Could not find '{MIDI_PORT_NAME}'. Did you enable it in Audio MIDI Setup?")
             return

        with mido.open_output(target_port) as midi_out:
            print(f"Forwarding MIDI to: {target_port}")
            print("Ready to play! Press Ctrl+C to stop.\n")

            while True:
                if ser.in_waiting >= 3:
                    midi_data = ser.read(3)
                    
                    status_byte = midi_data[0]
                    note = midi_data[1]
                    velocity = midi_data[2]

                    if status_byte == 144: # Note On
                        msg = mido.Message('note_on', note=note, velocity=velocity)
                        midi_out.send(msg)
                        print(f"Strum: Note {note} ON")
                        
                    elif status_byte == 128: # Note Off
                        msg = mido.Message('note_off', note=note, velocity=velocity)
                        midi_out.send(msg)
                        print(f"Mute: Note {note} OFF")

    except serial.SerialException:
        print(f"Error: Could not open {SERIAL_PORT}. Is the Arduino IDE Serial Monitor closed?")
    except KeyboardInterrupt:
        print("\nClosing bridge.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == '__main__':
    main()
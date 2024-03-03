if __name__ == '__main__':
    import PySimpleGUI as sg
    import scipy.signal as signal
    import soundfile as sf
    import numpy as np
    import matplotlib.pyplot as plt

    # Set the color theme for the GUI
    sg.theme('SystemDefault')

    # Define the GUI layout
    layout = [[sg.TabGroup([
        [sg.Tab('File Selection', [
            [sg.Text("Select an audio file:")],
            [sg.Input(key="-FILE-"), sg.FileBrowse(button_color=('white', 'darkblue'))],
        ])],
        [sg.Tab('Filter Selection', [
            [sg.Text("Select a filter type:")],
            [sg.Checkbox("Low-pass", key="-LPF-"), sg.Text("Enter the cutoff frequency (in Hz):"),
             sg.Input(key="-FREQ_LPF-", size=(10, 1))],
            [sg.Checkbox("High-pass", key="-HPF-"), sg.Text("Enter the cutoff frequency (in Hz):"),
             sg.Input(key="-FREQ_HPF-", size=(10, 1))],
            [sg.Text("Enter the order of the filter:")],
            [sg.Input(key="-ORDER-", size=(10, 1))],
        ])]
    ])],
        [sg.Button("Filter", button_color=('white', 'darkblue')), sg.Button("Exit", button_color=('white', 'darkblue'))],
        [sg.Text(size=(40, 1), key='-OUTPUT-')],
        [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='-PROGRESS-')]
    ]

    # Create the GUI window
    window = sg.Window("Audio Filter", layout)

    # Event loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "Filter":
            # Get the user input
            file = values["-FILE-"]
            lpf = values["-LPF-"]
            hpf = values["-HPF-"]
            freq_lpf = float(values["-FREQ_LPF-"]) if lpf else None
            freq_hpf = float(values["-FREQ_HPF-"]) if hpf else None
            order = int(values["-ORDER-"])

            # Read the audio file
            data, samplerate = sf.read(file)
            # Convert to mono if stereo
            if data.ndim == 2:
                data = data.mean(axis=1)
            # Get the time axis
            time = np.arange(len(data)) / samplerate

            # Compute the FFT of the original signal
            freqs = np.fft.rfftfreq(len(data), 1 / samplerate)
            fft = np.fft.rfft(data)

            # Design the filter
            if lpf:
                b, a = signal.butter(order, freq_lpf, "low", fs=samplerate)
                filtered_data_lpf = signal.filtfilt(b, a, data)
                filtered_fft_lpf = np.fft.rfft(filtered_data_lpf)
                new_file_lpf = file[:-4] + "_lowpass_filtered.wav"
                sf.write(new_file_lpf, filtered_data_lpf, samplerate)
                sg.popup(f"Low-pass filtered audio file saved as {new_file_lpf}")
            if hpf:
                b, a = signal.butter(order, freq_hpf, "high", fs=samplerate)
                filtered_data_hpf = signal.filtfilt(b, a, data)
                filtered_fft_hpf = np.fft.rfft(filtered_data_hpf)
                new_file_hpf = file[:-4] + "_highpass_filtered.wav"
                sf.write(new_file_hpf, filtered_data_hpf, samplerate)
                sg.popup(f"High-pass filtered audio file saved as {new_file_hpf}")

            # Update progress bar
            window['-OUTPUT-'].update('Filtering in progress...')
            window['-PROGRESS-'].update_bar(500)

            # Plot the original and filtered signals in time domain
            if lpf:
                plt.figure(1)
                plt.subplot(2, 1, 1)
                plt.plot(time, data, label='Original')
                plt.plot(time, filtered_data_lpf, label='Low-pass Filtered')
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude")
                plt.title("Signal in Time Domain (Low-pass Filtered)")
                plt.legend()
                plt.show(block=False)

                plt.subplot(2, 1, 2)
                plt.plot(freqs, np.abs(fft), label='Original')
                plt.plot(freqs, np.abs(filtered_fft_lpf), label='Low-pass Filtered')
                plt.xlabel("Frequency (Hz)")
                plt.ylabel("Magnitude")
                plt.title("Signal in Frequency Domain (Low-pass Filtered)")
                plt.legend()
                plt.show(block=False)
            if hpf:
                plt.figure(2)
                plt.subplot(2, 1, 1)
                plt.plot(time, data, label='Original')
                plt.plot(time, filtered_data_hpf, label='High-pass Filtered')
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude")
                plt.title("Signal in Time Domain (High-pass Filtered)")
                plt.legend()
                plt.show(block=False)

                plt.subplot(2, 1, 2)
                plt.plot(freqs, np.abs(fft), label='Original')
                plt.plot(freqs, np.abs(filtered_fft_hpf), label='High-pass Filtered')
                plt.xlabel("Frequency (Hz)")
                plt.ylabel("Magnitude")
                plt.title("Signal in Frequency Domain (High-pass Filtered)")
                plt.legend()
                plt.show(block=False)

            # Update progress bar
            window['-OUTPUT-'].update('Filtering completed.')
            window['-PROGRESS-'].update_bar(1000)

    # Close the GUI window
    window.close()

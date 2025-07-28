import numpy as np
import tensorflow as tf
from scipy.signal import resample
import numpy as np
import os
import wfdb
from scipy import signal
import neurokit2 as nk
import biosppy.signals.ecg as ecg
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# Load model once at import
model = tf.keras.models.load_model('enhanced_model_resaved.h5', compile=False)

def filter_data(val):
    """
    Filtre le signal ECG avec un filtre passe-bande

    Args:
        val: Signal ECG

    Returns:
        Signal ECG filtré
    """
    ecg_signal = val
    Fs = 500  
    N = ecg_signal.shape[1]
    t = ((np.linspace(0, N - 1, N)) / (Fs))
    cover = t.shape[0]
    t = t.reshape(1, cover)
    n = 2  

    Fcutoff_low = 0.5
    Wn_low = ((2 * Fcutoff_low) / (Fs))
    b_low, a_low = signal.butter(n, Wn_low, 'high')
    xn_filtered_LF = signal.filtfilt(b_low, a_low, ecg_signal)

    Fcutoff_high = 40
    Wn_high = ((2 * Fcutoff_high) / (Fs))
    b_high, a_high = signal.butter(n, Wn_high, 'low')
    xn_filtered_HF = signal.filtfilt(b_high, a_high, xn_filtered_LF)

    return xn_filtered_HF


def return_peaks(ecg_test):
    """
    Détecte les pics et intervalles importants dans le signal ECG

    Args:
        ecg_test: Signal ECG

    Returns:
        Signal nettoyé et informations sur les pics ou 'INCOMPLETE' si pas assez de pics
    """
    try:
        cleaned = nk.ecg_clean(ecg_test, sampling_rate=500)

        rdet, = ecg.hamilton_segmenter(signal=cleaned, sampling_rate=500)
        rdet, = ecg.correct_rpeaks(signal=cleaned, rpeaks=rdet, sampling_rate=500, tol=0.05)

        if (rdet.size <= 4):
            return 'INCOMPLETE'

        if len(rdet) >= 2:
            rdet = np.delete(rdet, -1)
            rdet = np.delete(rdet, 0)
            rpeaks = {'ECG_R_Peaks': rdet}
        else:
            return 'INCOMPLETE'

        cleaned_base = nk.signal_detrend(cleaned, order=0)

        signals, waves = nk.ecg_delineate(cleaned_base, rpeaks, sampling_rate=500, method="dwt")

        if (waves['ECG_T_Peaks'] is None):
            return 'INCOMPLETE'
        elif (waves['ECG_R_Onsets'] is None):
            return 'INCOMPLETE'
        elif (waves['ECG_R_Offsets'] is None):
            return 'INCOMPLETE'

        rpeakss = rpeaks.copy()
        temppo = 4 - len(rpeakss['ECG_R_Peaks'])

        if temppo > 0:
            for i in range(temppo):
                rpeakss['ECG_R_Peaks'] = np.append(rpeakss['ECG_R_Peaks'], rpeakss['ECG_R_Peaks'][-1] + 1)

        signals1, waves1 = nk.ecg_delineate(cleaned_base, rpeakss, sampling_rate=500, method="peak")

        if waves1['ECG_Q_Peaks'] is None:
            return 'INCOMPLETE'

        if temppo > 0:
            if len(waves1['ECG_Q_Peaks']) > temppo:
                for j in range(temppo):
                    waves1['ECG_Q_Peaks'] = waves1['ECG_Q_Peaks'][:-1]

        return (
            cleaned_base, [waves['ECG_T_Peaks'], waves['ECG_R_Onsets'], waves['ECG_R_Offsets'], waves1['ECG_Q_Peaks']])

    except Exception:
        return 'INCOMPLETE'


def extract_features_from_signal(signal_data):
    """
    Extrait les caractéristiques d'un signal ECG à 12 dérivations

    Args:
        signal_data: Signal ECG à 12 dérivations

    Returns:
        Liste de caractéristiques ou None si l'extraction échoue
    """
    
    if isinstance(signal_data, list):
        signal_data = np.array(signal_data)

    value = signal_data.T
    temp_list = []

    for ind in range(12):
        val_ind = value[ind]
        tmpp = val_ind.shape[0]
        val_ind = val_ind.reshape(1, tmpp)
        val_filtered = filter_data(val_ind)
        val_filtered = val_filtered.reshape(val_filtered.shape[1], )

        a_var = return_peaks(val_filtered)

        if a_var == 'INCOMPLETE':
            return None

        temp_list.append(a_var)

    if len(temp_list) != 12:
        return None

    features_list = []

    mini = float('inf')
    for check_index3 in range(12):
        for second_ind3 in range(4):
            if temp_list[check_index3][1][second_ind3] is None:
                return None
            mini = min(mini, len(temp_list[check_index3][1][second_ind3]))

    if mini == float('inf') or mini == 0:
        return None

    to_take = min(16, mini)

    for x in range(to_take):
        a_temp_list = []
        valid_beat = True

        for y in range(12):
            try:
                if (x >= len(temp_list[y][1][0]) or
                        x >= len(temp_list[y][1][1]) or
                        x >= len(temp_list[y][1][2]) or
                        x >= len(temp_list[y][1][3]) or
                        np.isnan(temp_list[y][1][1][x]) or
                        np.isnan(temp_list[y][1][2][x]) or
                        np.isnan(temp_list[y][1][3][x]) or
                        np.isnan(temp_list[y][1][0][x])):
                    valid_beat = False
                    break

                
                first_feat = temp_list[y][0][int(temp_list[y][1][1][x])] - temp_list[y][0][
                    int(temp_list[y][1][2][x])]
                
                second_feat = temp_list[y][0][int(temp_list[y][1][3][x])]

                third_feat = temp_list[y][0][int(temp_list[y][1][0][x])]

                a_temp_list.append(first_feat)
                a_temp_list.append(second_feat)
                a_temp_list.append(third_feat)
            except (IndexError, ValueError):
                valid_beat = False
                break

        if valid_beat and len(a_temp_list) == 36:  
            features_list.append(a_temp_list)

    if not features_list:
        return None

    features_array = np.array(features_list)
    features_array = features_array.reshape((features_array.shape[0], features_array.shape[1], 1))

    return features_array


def try_alternative_processing(signal_data):
    """
    Tente un traitement alternatif pour les signaux ECG difficiles

    Args:
        signal_data: Signal ECG à 12 dérivations

    Returns:
        Caractéristiques extraites ou None si l'extraction échoue
    """
    smoothed_signal = np.zeros_like(signal_data)
    for i in range(signal_data.shape[1]):
        smoothed_signal[:, i] = signal.savgol_filter(signal_data[:, i], 15, 3)

    normalized_signal = np.zeros_like(smoothed_signal)
    for i in range(smoothed_signal.shape[1]):
        signal_col = smoothed_signal[:, i]
        signal_range = np.max(signal_col) - np.min(signal_col)
        if signal_range > 0: 
            normalized_signal[:, i] = (signal_col - np.min(signal_col)) / signal_range
        else:
            normalized_signal[:, i] = signal_col

    return extract_features_from_signal(normalized_signal)


def predict_ecg(model, signal_data):
    """
    Prédit la classe d'un signal ECG

    Args:
        model: Modèle Keras chargé
        signal_data: Signal ECG à 12 dérivations

    Returns:
        Prédiction finale (0 ou 1)
    """
    features = extract_features_from_signal(signal_data)

    if features is None:
        features = try_alternative_processing(signal_data)

    if features is None:
        return None

    predictions = model.predict(features, verbose=0)

    beat_predictions = [1 if pred > 0.5 else 0 for pred in predictions]
    final_prediction = 1 if sum(beat_predictions) > len(beat_predictions) / 2 else 0

    return final_prediction



def predict_signal(signal, model=model):

    prediction = predict_ecg(model, signal)
    if prediction is not None:
        print("RÉSULTAT:")
        if prediction == 1:
            predicted_class = "MI"
        else:
            predicted_class = "NORM"
        print(f"{predicted_class}")
    else:
        print("RÉSULTAT: ÉCHEC")

    return prediction

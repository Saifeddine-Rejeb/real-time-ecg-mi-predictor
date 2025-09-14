import numpy as np
import pandas as pd
import tensorflow as tf
from scipy import signal as scipy_signal
from scipy.interpolate import interp1d
from scipy.signal import resample, butter, filtfilt
from scipy import stats
import os
import json
import warnings
from typing import Tuple, Dict, Optional

warnings.filterwarnings('ignore')


class SelfAttention(tf.keras.layers.Layer):
    def __init__(self, attention_dim=128, **kwargs):
        super(SelfAttention, self).__init__(**kwargs)
        self.attention_dim = attention_dim

    def build(self, input_shape):
        self.W_q = self.add_weight(
            name='query_weight',
            shape=(input_shape[-1], self.attention_dim),
            initializer='glorot_uniform',
            trainable=True
        )
        self.W_k = self.add_weight(
            name='key_weight',
            shape=(input_shape[-1], self.attention_dim),
            initializer='glorot_uniform',
            trainable=True
        )
        self.W_v = self.add_weight(
            name='value_weight',
            shape=(input_shape[-1], self.attention_dim),
            initializer='glorot_uniform',
            trainable=True
        )
        super(SelfAttention, self).build(input_shape)

    def call(self, inputs):
        Q = tf.keras.backend.dot(inputs, self.W_q)
        K_mat = tf.keras.backend.dot(inputs, self.W_k)
        V = tf.keras.backend.dot(inputs, self.W_v)

        attention_scores = tf.keras.backend.batch_dot(Q, K_mat, axes=[2, 2])
        attention_scores = attention_scores / tf.keras.backend.sqrt(
            tf.keras.backend.cast(self.attention_dim, dtype='float32'))

        attention_weights = tf.keras.backend.softmax(attention_scores)
        attended_values = tf.keras.backend.batch_dot(attention_weights, V)

        return attended_values

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], self.attention_dim)

    def get_config(self):
        config = super().get_config()
        config.update({"attention_dim": self.attention_dim})
        return config


class ECGSingleFileProcessor:

    def __init__(self, model_path: str, longueur_cible: int = 187, freq_echantillonnage: int = 360):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle non trouvé: {model_path}")

        custom_objects = {'SelfAttention': SelfAttention}
        self.model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)

        self.longueur_cible = longueur_cible
        self.freq_echantillonnage = freq_echantillonnage
        self.statistiques_normalisation = {}

        self.class_names = {
            0: "Normal",
            1: "Insuffisance_Legere",
            2: "Insuffisance_Moderee",
            3: "Insuffisance_Severe",
            4: "Insuffisance_Possible"
        }

        self.class_full_names = {
            0: "Pas d'Insuffisance Cardiaque",
            1: "Insuffisance Cardiaque Légère",
            2: "Insuffisance Cardiaque Modérée",
            3: "Insuffisance Cardiaque Sévère",
            4: "Insuffisance Cardiaque Possible"
        }

    def charger_signal_dat(self, chemin_fichier_dat: str) -> np.ndarray:
        try:
            with open(chemin_fichier_dat, 'rb') as f:
                donnees_brutes = f.read()

            signal_int16 = np.frombuffer(donnees_brutes, dtype=np.int16)
            signal_mv = signal_int16.astype(np.float64) / 1000.0

            return signal_mv

        except Exception as e:
            return None

    def lire_header_info(self, chemin_fichier_hea: str) -> Dict:
        info = {}

        try:
            with open(chemin_fichier_hea, 'r', encoding='utf-8') as f:
                lignes = f.readlines()

            premiere_ligne = lignes[0].strip().split()
            info['nom_enregistrement'] = premiere_ligne[0]
            info['nb_signaux'] = int(premiere_ligne[1])
            info['frequence'] = int(premiere_ligne[2])
            info['nb_echantillons'] = int(premiere_ligne[3])

            for ligne in lignes:
                if ligne.startswith('#'):
                    if 'Age:' in ligne:
                        info['age'] = ligne.split(':')[1].strip().split()[0]
                    elif 'Sexe:' in ligne:
                        info['sexe'] = ligne.split(':')[1].strip()
                    elif 'Diagnostic:' in ligne:
                        info['diagnostic'] = ligne.split(':', 1)[1].strip()

            return info

        except Exception as e:
            return {}

    def filtrer_signal_ecg(self, signal: np.ndarray, freq_ech: int = None) -> np.ndarray:
        if freq_ech is None:
            freq_ech = self.freq_echantillonnage

        try:
            sos_bandpass = scipy_signal.butter(4, [0.5, 40], btype='band', fs=freq_ech, output='sos')
            signal_filtre = scipy_signal.sosfilt(sos_bandpass, signal)

            sos_notch = scipy_signal.iirnotch(50, 30, fs=freq_ech)
            signal_filtre = scipy_signal.filtfilt(sos_notch[0], sos_notch[1], signal_filtre)

            return signal_filtre
        except:
            return signal

    def supprimer_derive_baseline(self, signal: np.ndarray, fenetre_mediane: int = 71) -> np.ndarray:
        try:
            baseline = scipy_signal.medfilt(signal, kernel_size=fenetre_mediane)
            signal_corrige = signal - baseline
            return signal_corrige
        except:
            return signal

    def reechantillonner_vers_longueur_cible(self, signal: np.ndarray) -> np.ndarray:
        longueur_originale = len(signal)

        if longueur_originale == self.longueur_cible:
            return signal

        try:
            signal_reechantillonne = resample(signal, self.longueur_cible)
            return signal_reechantillonne
        except:
            indices_originaux = np.linspace(0, longueur_originale - 1, longueur_originale)
            indices_cibles = np.linspace(0, longueur_originale - 1, self.longueur_cible)

            interpolateur = interp1d(indices_originaux, signal, kind='linear')
            signal_reechantillonne = interpolateur(indices_cibles)

            return signal_reechantillonne

    def supprimer_outliers(self, signal: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        try:
            z_scores = np.abs(stats.zscore(signal))
            outliers_mask = z_scores < threshold

            if np.sum(~outliers_mask) > 0:
                signal_clean = signal.copy()
                outlier_indices = np.where(~outliers_mask)[0]

                for idx in outlier_indices:
                    if idx > 0 and idx < len(signal) - 1:
                        signal_clean[idx] = (signal[idx - 1] + signal[idx + 1]) / 2

                return signal_clean

            return signal
        except:
            return signal

    def normaliser_vers_format_dataset(self, signal: np.ndarray, methode: str = "min_max") -> np.ndarray:
        if methode == "min_max":
            signal_min = np.min(signal)
            signal_max = np.max(signal)

            if signal_max - signal_min > 0:
                signal_normalise = (signal - signal_min) / (signal_max - signal_min)
            else:
                signal_normalise = np.zeros_like(signal)

            self.statistiques_normalisation = {
                "methode": "min_max",
                "min_original": float(signal_min),
                "max_original": float(signal_max),
                "amplitude": float(signal_max - signal_min)
            }

        elif methode == "z_score":
            signal_std = (signal - np.mean(signal)) / np.std(signal)
            signal_min = np.min(signal_std)
            signal_max = np.max(signal_std)
            signal_normalise = (signal_std - signal_min) / (signal_max - signal_min)

            self.statistiques_normalisation = {
                "methode": "z_score",
                "moyenne": float(np.mean(signal)),
                "ecart_type": float(np.std(signal))
            }

        signal_normalise = np.clip(signal_normalise, 0, 1)
        return signal_normalise

    def preprocesser_signal_complet(self, chemin_base: str) -> Tuple[np.ndarray, Dict]:
        chemin_dat = chemin_base + '.dat'
        chemin_hea = chemin_base + '.hea'

        if not os.path.exists(chemin_dat):
            return None, {}

        if not os.path.exists(chemin_hea):
            return None, {}

        signal_original = self.charger_signal_dat(chemin_dat)
        if signal_original is None:
            return None, {}

        metadonnees = self.lire_header_info(chemin_hea)
        freq_ech = metadonnees.get('frequence', self.freq_echantillonnage)

        if len(signal_original.shape) > 1 or len(signal_original) % 2 == 0:
            if len(signal_original) % 2 == 0:
                signal_original = signal_original.reshape(-1, 2)
                signal_original = np.mean(signal_original, axis=1)

        signal_filtre = self.filtrer_signal_ecg(signal_original, freq_ech)
        signal_sans_derive = self.supprimer_derive_baseline(signal_filtre)
        signal_clean = self.supprimer_outliers(signal_sans_derive)
        signal_reechantillonne = self.reechantillonner_vers_longueur_cible(signal_clean)
        signal_normalise = self.normaliser_vers_format_dataset(signal_reechantillonne)

        metadonnees.update({
            "longueur_originale": len(signal_original),
            "longueur_finale": len(signal_normalise),
            "statistiques_normalisation": self.statistiques_normalisation
        })

        return signal_normalise, metadonnees

    def predire_classe(self, signal_normalise: np.ndarray) -> Tuple[int, float, np.ndarray]:
        try:
            signal_pour_modele = signal_normalise.reshape(1, -1, 1)
            predictions_proba = self.model.predict(signal_pour_modele, verbose=0)
            predicted_class = np.argmax(predictions_proba[0])
            confidence = np.max(predictions_proba[0])

            return predicted_class, confidence, predictions_proba[0]

        except Exception as e:
            return None, 0.0, None

    def analyser_fichier_complet(self, chemin_base: str) -> Dict:
        signal_normalise, metadonnees = self.preprocesser_signal_complet(chemin_base)

        if signal_normalise is None:
            return {
                'success': False,
                'error': 'Échec du prétraitement',
                'file_path': chemin_base
            }

        predicted_class, confidence, all_probabilities = self.predire_classe(signal_normalise)

        if predicted_class is None:
            return {
                'success': False,
                'error': 'Échec de la prédiction',
                'file_path': chemin_base
            }

        results = {
            'success': True,
            'file_path': chemin_base,
            'filename': os.path.basename(chemin_base),
            'predicted_class': predicted_class,
            'predicted_class_name': self.class_names[predicted_class],
            'predicted_full_name': self.class_full_names[predicted_class],
            'confidence': confidence,
            'all_probabilities': all_probabilities,
            'signal_preprocessed': signal_normalise,
            'metadata': metadonnees,
            'preprocessing_stats': self.statistiques_normalisation
        }

        self.afficher_resultats(results)
        return results

    def afficher_resultats(self, results: Dict):
        print(f"Fichier analysé: {results['filename']}")
        print(f"Classe prédite: {results['predicted_class_name']}")
        print(f"Description: {results['predicted_full_name']}")
        print(f"Confiance: {results['confidence']:.3f}")
        print("-" * 50)
        print("Probabilités pour toutes les classes:")

        class_probs = []
        for i, prob in enumerate(results['all_probabilities']):
            class_probs.append((i, self.class_names[i], self.class_full_names[i], prob))

        class_probs.sort(key=lambda x: x[3], reverse=True)

        for i, (class_id, class_name, full_name, prob) in enumerate(class_probs):
            print(f"  {class_name}: {prob:.3f}")

        print("-" * 50)

    def predict_from_array(self, array: np.ndarray, preprocess: bool = True, normalisation_method: str = "min_max") -> dict:
        if not isinstance(array, np.ndarray):
            raise ValueError("Input must be a numpy array.")
        arr = array.squeeze()
        if preprocess:
            arr = self.supprimer_outliers(arr)
            arr = self.reechantillonner_vers_longueur_cible(arr)
            arr = self.normaliser_vers_format_dataset(arr, methode=normalisation_method)
        result = {}
        pred = self.predire_classe(arr)
        if pred[0] is not None:
            result['predicted_class'] = int(pred[0])
            result['predicted_class_name'] = self.class_names[pred[0]]
            result['predicted_full_name'] = self.class_full_names[pred[0]]
            result['confidence'] = float(pred[1])
            result['all_probabilities'] = pred[2]
        else:
            result['error'] = 'Prediction failed.'
        return result


def analyser_fichier_ecg_unique(chemin_base: str,
                                model_path: str = "best_ecg_hybrid_model.h5") -> Dict:
    try:
        processor = ECGSingleFileProcessor(model_path)
        results = processor.analyser_fichier_complet(chemin_base)
        return results

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file_path': chemin_base
        }


if __name__ == "__main__":
    #chemin_fichier = r"patients_test\Mild_Cardiac_Insufficiency\patient_classe_0_020"
    #chemin_fichier = r"patients_test\Moderate_Cardiac_Insufficiency\patient_classe_0_009"
    #chemin_fichier = r"patients_test\Possible_Cardiac_Insufficiency\patient_classe_1_746"
    #chemin_fichier = r"patients_test\No_Cardiac_Insufficiency\patient_classe_4_529"
    chemin_fichier = r"patients_test\Severe_Cardiac_Insufficiency\patient_classe_3_374"
    modele = "best_ecg_hybrid_model.h5"

    resultats = analyser_fichier_ecg_unique(
        chemin_base=chemin_fichier,
        model_path=modele
    )    

    if resultats['success']:
        print(f"Analyse terminée avec succès!")
    else:
        print(f"Erreur: {resultats['error']}")

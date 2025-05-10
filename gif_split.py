from PIL import Image, ImageSequence
import os

def split_gif(gif_path, output_folder):
    # Ouvrir le GIF
    gif = Image.open(gif_path)

    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Parcourir chaque frame du GIF
    for i, frame in enumerate(ImageSequence.Iterator(gif)):
        # Sauvegarder chaque frame en tant qu'image individuelle
        frame.save(os.path.join(output_folder, f"frame_{i:03d}.png"))

# Exemple d'utilisation
gif_path = "VZvx.gif"  # Remplacez par le chemin de votre GIF
output_folder = "path_to_output_folder"  # Remplacez par le chemin de votre dossier de sortie
split_gif(gif_path, output_folder)

from fastapi import FastAPI, UploadFile, File
import uvicorn
import tempfile
import essentia.standard as es

app = FastAPI()

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp.flush()
        path = tmp.name

    # Load audio
    loader = es.MonoLoader(filename=path)
    audio = loader()

    # BPM
    rhythm = es.RhythmExtractor2013(method="multifeature")
    bpm, beats, _, _, _ = rhythm(audio)

    # Key detection
    key_detector = es.KeyExtractor()
    key, scale, strength = key_detector(audio)

    # Loudness
    loudness_extractor = es.LoudnessEBUR128()
    integrated, _, _, _ = loudness_extractor(audio)

    # MFCC
    mfcc = es.MFCC()
    mfcc_bands, mfcc_coeffs = mfcc(audio)

    # Spectral centroid
    spectrum = es.Spectrum()(audio)
    centroid = es.Centroid()(spectrum)

    # Tonal centroid
    tonal_centroid = es.TonalExtractor()(audio)["tonal.centroid"]

    # Onset rate
    onset = es.OnsetRate()(audio)

    result = {
        "bpm": bpm,
        "key": key,
        "scale": scale,
        "key_strength": strength,
        "loudness": integrated,
        "spectral_centroid": float(centroid),
        "onset_rate": float(onset),
        "tonal_centroid": tonal_centroid.tolist(),
        "mfcc": mfcc_coeffs.tolist(),
        "instruments": ["guitar", "drums", "bass"]
    }

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

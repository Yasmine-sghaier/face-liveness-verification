dentity Verification Service (Face + Liveness) : Implémentation d’un système de vérification d’identité en temps réel basé sur la reconnaissance faciale et capture caméra avec FastAPI et DeepFace.

Ce service permet de vérifier l’identité d’un utilisateur en combinant :

Capture vidéo via caméra
Détection de présence réelle (liveness detection) -Vérification biométrique du visage . Liveness Detection (Anti-fraude)
Permet de vérifier que :

la personne est réellement présente devant la caméra et non une :photo , vidéo , écran , deepfake

 La détection de vie consiste à déterminer si le visage est celui d’un humain réel ou d’un spoof (attaque) 2. Face Verification (1:1)

Compare :

une image de référence (photo de profil) et une image capturée en temps réel

 L’objectif est de vérifier si les deux visages appartiennent à la même personne. 
Fonctionnement du système

Le processus global :

Ouverture de la caméra
Capture de plusieurs frames
Analyse du mouvement (liveness)
Si OK → comparaison avec photo de profil
Retour : verified / not verified
cd > backend : uvicorn app.main:app --reload
cd > fontend python -m http.server 5500 Ouvrir dans navigateur
👉 http://localhost:5500

Technologies & Modèles utilisés : Backend Framework API : FastAPI → API rapide pour gérer les requêtes /verify Serveur ASGI : Uvicorn → Exécute le backend en local  Computer Vision Traitement image : OpenCV → Capture et manipulation des frames vidéo  Intelligence Artificielle (Face Recognition) Lib principale : DeepFace
 Fournit :

détection de visage extraction d’empreinte faciale (embedding) comparaison entre deux visages
Modèles IA utilisés
🔹 1. FaceNet Modèle par défaut utilisé par DeepFace Transforme un visage en vecteur numérique (embedding) Permet de mesurer la similarité entre deux visages
🔹 2. RetinaFace Détecte automatiquement le visage dans l’image Gère : position du visage alignement landmarks (yeux, nez, bouche) 
 Principe de comparaison

👉 Le système repose sur :

extraction des features (embedding) calcul de distance (cosine / euclidienne)

👉 basé sur le concept de : Cosine Similarity

🌐 Frontend Camera API : WebRTC → Accès à la caméra utilisateur Langages : HTML JavaScript 🔄 Pipeline global Camera → Capture image → Backend → DeepFace → Face Detection (RetinaFace) → Feature Extraction (FaceNet) → Distance Calculation → Result (verified / false)

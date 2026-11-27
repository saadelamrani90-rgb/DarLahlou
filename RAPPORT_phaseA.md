# Dar Slimani : rapport de la phase A (tranche verticale)

Livrable : `render/sceneA_v1.mp4`. INT. MARCHÉ DE GROS, MATIN, 89 s, 1080p, 24 fps, 11 plans,
voix témoin synchronisées (lip sync Rhubarb), sous-titres en darija (alphabet latin) et en français.

## Coûts mesurés
- Rendu : 1 073 images (animation « en deux », 12 poses par seconde) en 36 min, soit 2,0 s par image sur 4 CPU, sans GPU.
- Dépense : 0 €. Blender, Rhubarb, edge-tts et ffmpeg sont gratuits, et la machine est incluse dans la session.
- Estimation pour un épisode de 20 min : environ 13 500 images, soit environ 7 h 30 de rendu, plus le temps d'écriture des plans.

## Ce qui marche
- Les 3 personnages sont reconnaissables en silhouette, et leurs proportions et couleurs restent identiques d'un plan à l'autre (mêmes scripts).
- Aucun scintillement : l'éclairage toon est calculé, pas simulé, donc l'image est identique à chaque rendu.
- La chaîne est entièrement scriptée et peut être rejouée : dialogue JSON, puis voix, puis formes de bouche, puis timeline, puis rendu, puis montage.
- Le gag de la tomate en classe affaires et l'insert du téléphone fonctionnent.

## Ce qui est faible
- Les voix témoin sont plates et ne jouent pas. Elles seront remplacées par les vocaux de Saad, comme prévu.
- La bouche de Brahim est petite sous la moustache : le lip sync est lisible, mais discret.
- La gestuelle est encore pauvre : tête, buste, regard, un bras. Les mains n'ont pas de doigts (le comptage se fait avec le bras entier).
- Pas encore de musique, d'ambiance sonore de marché ni de figurant (le fellah).
- Les plans sont écrits en Python : c'est rapide pour moi, mais personne d'autre ne peut encore les modifier.

## À changer avant la phase B
1. Intégrer les vocaux de Saad et relancer Rhubarb. Le reste de la chaîne ne change pas.
2. Ajouter des mains avec des doigts simples et une bibliothèque de poses réutilisables (pointer, compter, bras croisés).
3. Ajouter l'ambiance sonore et un thème musical original, avec une licence vérifiée.
4. Décrire chaque scène dans un storyboard JSON, sans code propre à chaque plan, pour tenir un épisode par semaine.

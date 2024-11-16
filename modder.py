import os, subprocess, shutil, json

APK = "BT.apk"
FOLDER = APK[:-4]

def decompile(file, folder):
    print(f"Decompiling {file} into {folder})")
    sp = subprocess.Popen(f"apktool d -f {file} -o {folder}", shell=True, stdin=subprocess.PIPE)
    sp.communicate(input=b'\n')

def recompile(file, folder):
    print(f"Recompiling {folder} into {file}")
    sp = subprocess.Popen(f"apktool b -f --use-aapt2 -d {folder} -o tmp.apk", shell=True, stdin=subprocess.PIPE)
    sp.communicate(input=b'\n')

    print(f"Aligning {file}")
    sp = subprocess.Popen(f"zipalign -p 4 tmp.apk tmp2.apk", shell=True, stdin=subprocess.PIPE)
    sp.communicate(input=b'\n')

    print(f"Signing {file}")
    sp = subprocess.Popen(f"ApkSigner sign --key res/index.pk8 --cert res/index.pem --v4-signing-enabled false --out modded.apk tmp2.apk", shell=True, stdin=subprocess.PIPE)
    sp.communicate(input=b'\n')

    os.remove(f"tmp.apk")
    os.remove(f"tmp2.apk")
    shutil.rmtree(folder)

def mod(name, config):
    decompile(APK, FOLDER)

    RESOURCES = f"{FOLDER}/assets/Resources"

    MODELS_PATH = f"{RESOURCES}/models"
    AUDIO_PATH = f"{RESOURCES}/audio"
    MODELS = {
        "ball": f"{MODELS_PATH}/simon/ball/ball.sgm",
        "blob": f"{MODELS_PATH}/simon/blob/blob.sgm",
        "racket": f"{MODELS_PATH}/simon/racket/racket-texturedrayne.sgm",
        "beach": f"{MODELS_PATH}/simon/ground/beachrayne.sgm",
        "radio": f"{MODELS_PATH}/uberpixel/radio.sgm",
        "water": f"{MODELS_PATH}/uberpixel/water.sgm",
        "bounds": f"{MODELS_PATH}/uberpixel/bounds.sgm"
    }
    TEXTURES = {
        "ball": f"{MODELS_PATH}/simon/ball/ballbacked.astc",
        "blob": f"{MODELS_PATH}/simon/blob/body.astc",
        "racket": f"{MODELS_PATH}/simon/racket/racketbaked.astc",
        "racket_net": f"{MODELS_PATH}/simon/racket/racketnet.astc",
        "ground_ball": f"{MODELS_PATH}/simon/ground/ballbacked.astc",
        "beach": f"{MODELS_PATH}/simon/ground/groundbaked.astc",
        "sky": f"{MODELS_PATH}/Optikz/sky_lightblue.astc",
        "palm_leaf": f"{MODELS_PATH}/simon/ground/palmleaf.astc",
        "wood": f"{MODELS_PATH}/simon/ground/wood.astc",
        "stump": f"{MODELS_PATH}/simon/ground/stump.astc",
        "noise": f"{MODELS_PATH}/simon/ground/noise.astc"
    }
    SOUNDS = {
        "ball_hit": f"{AUDIO_PATH}/Oculus/ballhit.ogg",
        "ball_ploink": f"{AUDIO_PATH}/othercc0/ploink.ogg",
        "ball_sand": f"{AUDIO_PATH}/Uberpixel/ball_sand.ogg",
        "ha": f"{AUDIO_PATH}/Uberpixel/ha.ogg",
        "woohoo": f"{AUDIO_PATH}/Uberpixel/woohoo.ogg",
        "shore": f"{AUDIO_PATH}/Oculus/shore.ogg",
        "noise": f"{AUDIO_PATH}/Uberpixel/noise.ogg",
        "song1": f"{AUDIO_PATH}/whatfunk/128heartbeats.ogg",
        "song2": f"{AUDIO_PATH}/whatfunk/justforyou.ogg",
        "song3": f"{AUDIO_PATH}/whatfunk/neverstop.ogg",
        "song4": f"{AUDIO_PATH}/whatfunk/silhouette.ogg"
    }

    assets = f"configs/{name}/"

    if "title_image" in config and config["title_image"] != "":
        shutil.copy(f"{assets}{config['title_image']}", f"{RESOURCES}/textures/title.png")

    if "font" in config and config["font"] != "":
        shutil.copy(f"{assets}{config['font']}", f"{RESOURCES}/fonts/NotoSans-Bold.ttf")

    if "models" in config:
        for model, target in MODELS.items():
            if model in config["models"] and config["models"][model] != "":
                path = config["models"][model]
                
                if path[-4:] != ".sgm":
                    print(f"Skipping {path} as it is not a .sgm file")
                    continue
                
                shutil.copy(f"{assets}{path}", f"{target}")

    if "textures" in config:
        for texture, target in TEXTURES.items():
            if texture in config["textures"] and config["textures"][texture] != "":
                path = config["textures"][texture]
                
                if path[-5:] != ".astc":
                    if path[-4:] != ".png":
                        print(f"Skipping {path} as it is not a .astc file or .png file")
                        continue
                    
                    print(f"Attempting to convert {path} to a .astc file")
                    if os.path.exists("res/bin/astcenc"):
                        os.system(f"res/bin/astcenc -cs {assets}{path} {assets}{path[:-4]}.astc 6x6 -fast")
                    elif os.path.exists("res/bin/astcenc-avx2.exe"):
                        os.system(f"res/bin/astcenc-avx2.exe -cs {assets}{path} {assets}{path[:-4]}.astc 6x6 -fast")
                    else:
                        continue
                    
                    path = f"{path[:-4]}.astc"
                
                shutil.copy(f"{assets}{path}", f"{target}")

    if "sounds" in config:
        for sound, target in SOUNDS.items():
            if sound in config["sounds"] and config["sounds"][sound] != "":
                path = config["sounds"][sound]
                
                if path[-4:] != ".ogg":
                    if path[-4] != ".":
                        print(f"Skipping {path} as it does not have a compatible extension")
                        continue
                    print(f"Attempting to convert {path} to a .ogg file")
                    os.system(f"ffmpeg -i {assets}{path} -c:a libvorbis -q:a 4 {assets}{path[:-4]}.ogg")
                    path = f"{path[:-4]}.ogg"
                
                shutil.copy(f"{assets}{path}", f"{target}")

    if os.path.exists(f"{FOLDER}/apktool.yml"):
        with open(f"{FOLDER}/apktool.yml", 'r') as f:
            filedata = f.read()
        
        filedata = filedata.replace('renameManifestPackage: null', f"renameManifestPackage: com.index.blobby_tennis_{name}")
        
        with open(f"{FOLDER}/apktool.yml", 'w') as f:
            f.write(filedata)

    recompile(APK, FOLDER)

    os.rename("modded.apk", f"out/blobby_tennis_{name}.apk")


def main():
    configs = [f for f in os.listdir('configs')]

    if not os.path.exists('out'):
        os.makedirs('out')

    for folder in configs:
        file = f"configs/{folder}/manifest.json"
        
        print("-" * 20)
        print(f"Generating {folder}")

        with open(file, 'r') as f:
            config = json.load(f)

        mod(folder, config)

        print(f"Completed {folder}")
    
    print("-" * 20)
    print("All mods completed")


if __name__ == "__main__":
    main()
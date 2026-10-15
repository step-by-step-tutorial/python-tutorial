<h1 align="center">DL Platform</h1>

Runs deep learning vision tasks on a folder of images. Every task shares one general core; a task only names the
labels it keeps. The first tasks detect vehicles, people and animals with a Faster R-CNN detector pre-trained on the
[COCO](https://cocodataset.org) dataset, so they need no training.

```text
Detection
    load the pre-trained detector (downloaded once into models/)
    find the images in data/{task}/
    detect the objects in each image and keep the task labels above the score threshold
    save each image with its boxes drawn to output/{task}/
    save every detection to output/{task}_detections.csv
```

| Task                | Labels                                                                   |
|---------------------|--------------------------------------------------------------------------|
| `vehicle_detection` | bicycle, car, motorcycle, bus, truck                                     |
| `person_detection`  | person                                                                   |
| `animal_detection`  | bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe        |

## Project Structure

```text
dl_platform
├── data/                     input images, one folder per task (not committed)
├── models/                   downloaded pre-trained weights (not committed)
├── output/                   annotated images and detection files (not committed)
├── audit_log/                execution logs (not committed)
├── src/dl_platform
│   ├── main.py               command line entry point
│   ├── config/               model types and detection tasks
│   ├── model/                all dataclasses: settings, task, detection, execution
│   ├── detector/             detector factory and object detector
│   ├── inference/            detection runner
│   ├── repository/           image and detection repositories
│   ├── visualize/            draws the detection boxes
│   ├── audit/                execution log
│   └── util/                 general helpers
├── tests
└── Dockerfile
```

All commands below run from the repository root.

## 1. Prerequisite

* Python 3.12+
* Internet access on the first run, to download the pre-trained weights
* Docker, only to run with Docker

```shell
python --version
pip --version
docker --version
```

## 2. Install

```shell
python -m pip install --upgrade pip
pip install -r ./dl_platform/requirements.txt
pip install -e ./dl_platform
```

On Linux without a GPU, install the smaller CPU build of PyTorch before the commands above:

```shell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## 3. Test

The tests use small generated images and an untrained detector, so they need no download.

```shell
pytest ./dl_platform
```

## 4. Add Images

Put `.jpg`, `.jpeg` or `.png` images in the folder of each task. These commands download a few sample images:

```shell
mkdir -p ./dl_platform/data/vehicle_detection ./dl_platform/data/person_detection ./dl_platform/data/animal_detection
curl -L -o ./dl_platform/data/vehicle_detection/bus.jpg https://github.com/ultralytics/assets/releases/download/v0.0.0/bus.jpg
curl -L -o ./dl_platform/data/person_detection/zidane.jpg https://github.com/ultralytics/assets/releases/download/v0.0.0/zidane.jpg
curl -L -o ./dl_platform/data/person_detection/bus.jpg https://github.com/ultralytics/assets/releases/download/v0.0.0/bus.jpg
curl -L -o ./dl_platform/data/animal_detection/dog1.jpg https://raw.githubusercontent.com/pytorch/vision/main/gallery/assets/dog1.jpg
curl -L -o ./dl_platform/data/animal_detection/dog2.jpg https://raw.githubusercontent.com/pytorch/vision/main/gallery/assets/dog2.jpg
```

## 5. Run

Pass the task name:

```shell
python -m dl_platform.main vehicle_detection
python -m dl_platform.main person_detection
python -m dl_platform.main animal_detection
```

Without arguments, the command asks for the task interactively. The first run downloads the pre-trained weights
into `dl_platform/models/`; later runs reuse them.

Each run writes:

```text
dl_platform/output/{task}/                     the images with their boxes drawn
dl_platform/output/{task}_detections.csv       one row per detection: image, label, score and box
dl_platform/audit_log/{task}_detect_{run_id}.csv
```

### 5.1. Configuration

| Variable                      | Default                 | Description                                         |
|-------------------------------|-------------------------|-----------------------------------------------------|
| `DL_PLATFORM_MODEL_TYPE`      | `faster_rcnn_mobilenet` | `faster_rcnn_mobilenet` (fast) or `faster_rcnn_resnet50` (more accurate) |
| `DL_PLATFORM_SCORE_THRESHOLD` | `0.5`                   | minimum confidence of a detection                   |
| `DL_PLATFORM_DEVICE`          | `cpu`                   | `cpu`, or `cuda` on a machine with a GPU            |
| `DL_PLATFORM_DATA_DIR`        | `data`                  | folder that holds one image folder per task         |
| `EXECUTION_LOG_ENABLED`       | `true`                  | write `audit_log/{task}_detect_{run_id}.csv`        |

```shell
DL_PLATFORM_MODEL_TYPE=faster_rcnn_resnet50 python -m dl_platform.main vehicle_detection
```

## 6. Run with Docker

The image uses the CPU build of PyTorch. The folders `data`, `models`, `output` and `audit_log` are mounted from
`dl_platform/`, so the images, the downloaded weights and the results stay on the host.

```shell
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev build dl-platform
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev run --rm dl-platform vehicle_detection
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev run --rm dl-platform person_detection
docker compose --file docker-compose.yml --project-name dev --env-file ./.env.dev run --rm dl-platform animal_detection
```

```shell
docker rmi samanalishiri/dl-platform:latest
```

## 7. Clean

```shell
rm -rf ./dl_platform/src/*.egg-info
rm -rf ./dl_platform/output ./dl_platform/audit_log
rm -rf ./dl_platform/models
```

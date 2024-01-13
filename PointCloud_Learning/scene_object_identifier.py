import torch
from torch.utils.data import DataLoader
from classes import PointNet, PointCloudData, default_transforms
import glob
from torchmetrics import Precision, Recall, F1Score


print("Beginning Object (from Scene) Classification ...")


classification_filenames = glob.glob('Part2_Test/Objects_off/*.off', recursive=True)

classification_batch_size=len(classification_filenames)

classification_ds = PointCloudData(valid=True, filenames=classification_filenames, transform=default_transforms)
classification_loader = DataLoader(dataset=classification_ds, batch_size=classification_batch_size)


classes = {"bowl": 0,
           "cap": 1,
           "cereal": 2,
           "coffee": 3,
           "soda": 4}


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

pointnet = PointNet()
pointnet.to(device)
pointnet.load_state_dict(torch.load('models/save.pth'))


pointnet.eval()
all_preds = []
all_gt_labels = []
with torch.no_grad():
    for i, data in enumerate(classification_loader):
        print('Batch [%4d / %4d]' % (i+1, len(classification_loader)))
        
        inputs, gt_labels = data['pointcloud'].float(), data['category']
        outputs, __, __ = pointnet(inputs.transpose(1,2))
        _, preds = torch.max(outputs.data, 1)
        all_preds += list(preds.numpy())
        all_gt_labels += list(gt_labels.numpy())



print("\nPredicted objects:\n")
for i, _ in enumerate(classification_filenames):
    print(str(i+1) + ": " + list(classes.keys())[list(classes.values()).index(all_preds[i])] + "\n")

print("\nGround Truth objects:\n")
for i, _ in enumerate(classification_filenames):
    print(str(i+1) + ": " + list(classes.keys())[list(classes.values()).index(all_gt_labels[i])] + "\n")


#--------------------------------------------------------------
# Metrics -----------------------------------------------------
#--------------------------------------------------------------

all_preds_np = []
all_gt_labels_np = []
for i, j in zip(all_preds, all_gt_labels):
    all_preds_np.append(i.item())
    all_gt_labels_np.append(j.item())


tensor_preds = torch.tensor(all_preds_np)
tensor_gt_labels = torch.tensor(all_gt_labels_np)


precision = Precision(task="multiclass", average='macro', num_classes=5)
recall = Recall(task="multiclass", average='macro', num_classes=5)
f1_score = F1Score(task="multiclass", num_classes=5)


print("Precision: {:.1f}%".format(float((precision(tensor_preds, tensor_gt_labels)).item() * 100)))
print("Recall: {:.1f}%".format(float((recall(tensor_preds, tensor_gt_labels)).item() * 100)))
print("F1 Score: {:.1f}%".format(float((f1_score(tensor_preds, tensor_gt_labels)).item() * 100)))
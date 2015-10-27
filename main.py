from os.path import basename

# Own packages
from learn import *
from features import *
from Load import *
from image_loader import *
from cross_validation import cross_validate
from MetaParameterEstimators import *


def train_and_predict(trainer_function, feature_combiner, number_of_pca_components=0, train_directories=['data/train'], test_directories=['data/test']):
    # Load data
    trainer = trainer_function()
    train_images = load(train_directories, True)
    test_images = load(test_directories, False)
    print('Images loaded')
    # Feature extraction
    feature_extraction(train_images, feature_combiner)
    feature_extraction(test_images, feature_combiner)
    print('Features extracted')
    # Feature transform
    train_data = [image.features for image in train_images]
    pca = None
    if number_of_pca_components > 0:
        pca = PCA(n_components=min(number_of_pca_components, len(train_images[0].features)))
        pca.fit(train_data)
        train_data = pca.transform(train_data)
    # Train model
    train_classes = [image.label for image in train_images]
    trainer.train(train_data, train_classes)
    print('Training complete!!')
    # Predict class of test images
    file = open('result.csv', 'w')
    file.write('Id,%s\n' % str.join(',', trainer.classes))
    for image in test_images:
        test_data = image.features
        if pca:
            test_data = pca.transform(test_data)
        predictions = trainer.predict_proba(test_data)
        identifier = int(os.path.splitext(basename(image.filename))[0])
        file.write('%d,%s\n' % (identifier, str.join(',', [('%.13f' % p) for p in predictions[0]])))
    file.close()

def trainFolds(directories):
    images = load(directories, True, permute=True)
    combiner = FeatureCombiner([HsvFeature(), DetectCircle(), HogFeature()])  # Feature selection
    trainer = LogisticRegressionTrainer  # Learning algorithm, make sure this is a function and not an object
    cross_validate(images, combiner, trainer, k=10, use_super_class=False, number_of_pca_components=0)  # use 10 folds, no pca

def featureTest(directories):
    images = load(directories, True, permute=False)
    combiner = ColorCenter()  # Feature selection
    trainer = GaussianNaiveBayes # Learning algorithm, make sure this is a function and not an object
    values = [combiner.process(im.image) for im in images if im.label == 'D10']
    values2 = [combiner.process(im.image) for im in images if im.label == 'B21']
    labels = ['D10','B21']
    from visualize import ScatterPlot
    plot =  ScatterPlot()
    plot.show(labels,[values,values2])

def estimateMetas(directories):
    meta_estimators = [estimateHogOrientationsParameters,estimateHogPixelsPerCellParameters,
                       estimateHogCellsPerBlockParameters, estimateRegionRatioParameters,
                       estimateDetectCircleParameters
                   ]

    for estimator in meta_estimators:
        estimator(directories)

#train_and_predict(trainer_function, FeatureCombiner([HsvFeature(), DetectCircle(), HogFeature()]), 0,
#                  ['data/train'],
#                  ['data/test'])

#trainFolds(['data/train'])
estimateMetas(['data/train'])
#trainFolds(['data/train/blue_circles','reversed_triangles'])
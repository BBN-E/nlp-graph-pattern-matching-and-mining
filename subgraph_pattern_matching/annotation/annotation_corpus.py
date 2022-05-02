
class AnnotationCorpus():

    def __init__(self, train_annotations, dev_annotations, test_annotations):
        '''

        :param train_annotations: list[annotation.annotation.Annotation]
        :param dev_annotations: list[annotation.annotation.Annotation]
        :param test_annotations: list[annotation.annotation.Annotation]
        '''

        self.train_annotations = train_annotations
        self.dev_annotations = dev_annotations
        self.test_annotations = test_annotations

    def get_categories(self):
        categories = set()
        for annotation in self.train_annotations:
            categories.add(annotation.category)

        return list(categories)

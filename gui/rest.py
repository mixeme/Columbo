
class Window(QMainWindow):
    # Snip...
    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        """
        def create_tree(path):
            model = QStandardItemModel()
            current = model.invisibleRootItem()

            #for root, dirs, files in os.walk(path):
            #    root.replace("\\", "/")
            #    if (root.startwith(current.__str__())):



            for d in dirs:
                current.appendRow(QStandardItem(d))
            for f in files:
                current.appendRow(QStandardItem(f))
            if len(dirs) == 0:
                current = current.parent()
            else:
                current = current.child(0)




            #return model
        """

        def createmodel(data):
            model = QStandardItemModel()
            root = model.invisibleRootItem()
            for i in data:
                root.appendRow(QStandardItem(i))
            return model

        def filewalk(fileNames, fileTreeView):
            path = fileNames[0]
            a = os.walk(path)
            b = a.__iter__().__next__()
            print(b)
            fileTreeView.setModel(createmodel(b[2]))
            for root, dirs, files in os.walk(path):
                print(root, dirs, files)

                """
                def create_tree(path):
                    model = QStandardItemModel()
                    current = model.invisibleRootItem()

                    #for root, dirs, files in os.walk(path):
                    #    root.replace("\\", "/")
                    #    if (root.startwith(current.__str__())):



                    for d in dirs:
                        current.appendRow(QStandardItem(d))
                    for f in files:
                        current.appendRow(QStandardItem(f))
                    if len(dirs) == 0:
                        current = current.parent()
                    else:
                        current = current.child(0)




                    #return model
                """

                def createmodel(data):
                    model = QStandardItemModel()
                    root = model.invisibleRootItem()
                    for i in data:
                        root.appendRow(QStandardItem(i))
                    return model

                def filewalk(fileNames, fileTreeView):
                    path = fileNames[0]
                    a = os.walk(path)
                    b = a.__iter__().__next__()
                    print(b)
                    fileTreeView.setModel(createmodel(b[2]))
                    for root, dirs, files in os.walk(path):
                        print(root, dirs, files)
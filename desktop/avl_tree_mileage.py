from desktop import acceleration_gyroscopic_data
from desktop.mileage_node import mileage_node



class avl_tree_mileage(object):

    def insert(self, root, mileage, data):

        if not root:
            return mileage_node(mileage, data)
        elif mileage < root.mileage:
            root.left = self.insert(root.left, mileage, data)
        else:
            root.right = self.insert(root.right, mileage, data)

        root.h = 1 + max(self.getHeight(root.left),
                         self.getHeight(root.right))

        b = self.getBal(root)

        if b > 1 and mileage < root.left.mileage:
            return self.rRotate(root)

        if b < -1 and mileage > root.right.mileage:
            return self.lRotate(root)

        if b > 1 and mileage > root.left.mileage:
            root.left = self.lRotate(root.left)
            return self.rRotate(root)

        if b < -1 and mileage < root.right.mileage:
            root.right = self.rRotate(root.right)
            return self.lRotate(root)

        return root

    def lRotate(self, z):

        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self.getHeight(z.left),self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left),self.getHeight(y.right))
        return y

    def rRotate(self, z):

        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self.getHeight(z.left),self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left), self.getHeight(y.right))
        return y

    def getHeight(self, root):
        if not root:
            return 0
        return root.height

    def getBal(self, root):
        if not root:
            return 0
        return self.getHeight(root.left) - self.getHeight(root.right)



    def preOrder(self, root):
        if root.left:
            yield from self.preOrder(root.left)
        yield root
        if root.right:
            yield from self.preOrder(root.right)



#Test

# tree = avl_tree_mileage()
# root = None
# mileages = [2,1,3,4,20,6,7,8,55]
# data_1 = acceleration_gyroscopic_data.acceleration_gyroscopic_data(1,1,1,1,1,1)
# for i in mileages:
#     root = tree.insert(root, i, data_1)
#
# for x in tree.preOrder(root):
#     print("At mileage: {}\n\t Acc[X,Y,Z]: {}\n\t Gyro[X,Y,Z]: {}".format(x.mileage, x.data.get_acceleration_cartesian(), x.data.get_gyro_cartesian()))

# -*- coding:utf-8 -*-

from random import randint
from math import sqrt

class KmeansAlgo:
	def __init__(self,filename):
		self.dataSet = self.read_from_file(filename)
		self.attr_num = len(self.dataSet[0])
		self.clusters = [] #k个簇
		self.means = []    #k个质心     [[],[],[],.....]

	def read_from_file(self,filename):
		dataSet = []
		ifile = open(filename)
		for line in ifile:
			data_item = []
			for item in line.strip().split(',')[0:-1]:
				data_item.append(float(item))
			dataSet.append(data_item)
		return dataSet

	def k_means(self,k):
		# 选取k个质心
		i = self.k = k
		selects = []
		while i > 0:
			i_select = randint(0,len(self.dataSet)-1)
			if selects.count(i_select) == 0:
				selects.append(i_select)
				self.means.append(self.dataSet[i_select])
				cluster = []
				self.clusters.append(cluster)
				i -= 1
		# 根据默认的质心，生成簇
		self.grow_clusters()

		old_var = -1
		new_var = self.get_var()
		while abs(new_var - old_var)>=1:
			# 重新计算质心
			for i_means in range(self.k):
				self.means[i_means] = self.get_means(i_means)
			# 清空簇
			for i_means in range(self.k):
				self.clusters[i_means] = []
			# 重新生成簇
			self.grow_clusters()
			old_var = new_var
			new_var = self.get_var()
			print(new_var)
		self.print_clusters()

	# 将所有的数据放入相应的簇中
	def grow_clusters(self):
		for i in range(len(self.dataSet)):
			label = self.clusterof(i)
			self.clusters[label].append(i)

	# 计算点到质心的欧式距离，m为self.means[]下标，i为点下标，attr_num为属性个数
	def get_dist(self,m,i):
		sum = 0
		for i_attr in range(self.attr_num):
			sum += (self.dataSet[i][i_attr]-self.means[m][i_attr])*(self.dataSet[i][i_attr]-self.means[m][i_attr])
		return sqrt(sum)

	# 根据质心决定点属于哪个簇
	def clusterof(self,i):
		dist = self.get_dist(0,i)  #初始化点到质心的距离为到第一个质心的距离
		label = 0
		tmp = 0.0
		for i_means in range(1,self.k):
			tmp = self.get_dist(i_means,i)
			if tmp < dist:
				dist = tmp
				label = i_means
		return label

	# 计算簇的SSE
	def get_var(self):
		var = 0.0
		for i_means in range(self.k):
			for i in self.clusters[i_means]:
				var += self.get_dist(i_means,i)
		return var

	# 计算当前簇的质心
	def get_means(self,i_means):
		new_mean = []
		data_num = len(self.clusters[i_means])   #簇的大小
		for i_attr in range(self.attr_num):
			new_mean.append(0.0)
		for i in self.clusters[i_means]:
			for i_attr in range(self.attr_num):
				new_mean[i_attr] += self.dataSet[i][i_attr]
		for i_attr in range(self.attr_num):
			new_mean[i_attr] /= data_num
		return new_mean

	def print_clusters(self):
		for i_means in range(self.k):
			print(self.clusters[i_means])

if __name__ == '__main__':
	ka = KmeansAlgo('DataSet/Seeds.txt')
	ka.k_means(5)



# -*- coding:utf-8 -*-

'''
[
	[1.0,2.0,3.0,4.0,Iris-versicolor],
	...
]
'''

# -*- coding:utf-8 -*-
from math import log
import random
import copy

class MiningSolution:
	def __init__(self,filename):
		self.split_type = 'INFOGAIN'      #   INFOGAIN:1 , GINI:2   ,  ERRORRATE:3
		self.prun_type = 'NOPRUN'       #   NOPRUN:1  ,  PREPRUN:2 , POSTPRUN:3
		self.transactions = self.ReadFromFile(filename)

# 初始化决策树和可选属性集
	def InitTree(self):
		self.attr_indexs = list(range(len(self.transactions[0])-1))
		self.decision_tree = dict()

# 修改划分属性选择模式
	def ChangeSplitMod(self,code):
		if code == 1:
			self.split_type = 'INFOGAIN'
		elif code == 2:
			self.split_type = 'GINI'
		elif code == 3:
			self.split_type = 'ERRORRATE'
		else:
			print('error splitMod code')
			exit()

# 修改剪枝策略
	def ChangePrunMod(self,code):
		if code == 1:
			self.prun_type = 'NOPRUN'
		elif code == 2:
			self.prun_type = 'PREPRUN'
		elif code == 3:
			self.prun_type = 'POSTPRUN'
		else:
			print('error prunMod code')
			exit()

	# read data from file
	def ReadFromFile(self,filename):
		transactions = []
		in_file = open(filename)
		try:		
			for line in in_file:
				transactions.append(line.strip().split(','))
		except:
			print("error when read file ",filename)
			in_file.close()
		return transactions

# 计算数据集的每个label的概率
	def CalcProbs(self,dataSet):
		dataSet_size = len(dataSet)
		lable_dict = dict()   #标签名：出现次数
		prob_list = list()    #标签名：出现频率
		for item in dataSet:
			cur_lable = item[-1]
			if cur_lable not in lable_dict.keys():
				lable_dict[cur_lable] = 0
			lable_dict[cur_lable] += 1
		for key in lable_dict:
			prob_list.append(float(lable_dict[key])/dataSet_size)
		return prob_list

# 计算数据集信息熵
	def CalcEntropy(self,probs):
		entropy = 0.0
		for prob in probs:
			entropy -= prob*log(prob,2)
		return entropy

# 计算数据集的Gini指数
	def CalcGini(self,probs):
		gini = 1.0
		for prob in probs:
			gini -= prob*prob
		return gini

# 计算数据集的错误率
	def CalcErrorRate(self,probs):
		# print(probs)
		if len(probs) == 0:
			return 0
		return 1-max(probs)

# 选择判断划分的方式
	def CalcMethod(self,dataSet):
		probs = self.CalcProbs(dataSet)
		# 如果采用信息增益判断最优划分的情况
		if self.split_type == 'INFOGAIN':
			return self.CalcEntropy(probs)
		# 如果采用GINI判断最优划分的情况
		elif self.split_type == 'GINI':
			return self.CalcGini(probs)
		# 如果采用c错误率判断最优划分的情况
		elif self.split_type == 'ERRORRATE':
			return self.CalcErrorRate(probs)

# 计算拥有最大信息增益的划分属性,   type表示采用哪种标准判断最优划分
	def SeletBestSplit(self,dataSet):
		calc_value = 1.0             
		best_index = -1
		best_split_value = 0
		sub_dataSet_1 = list()
		sub_dataSet_2 = list()
		for i in self.attr_indexs:#遍历数据集的每个可用属性
			attr_list = [example[i] for example in dataSet]
			uniq_values = set(attr_list)
			for thld in uniq_values:
				sub_dataSet_1_1,sub_dataSet_2_2 = self.SplitDataSet(dataSet,i,thld)  #得到小于阈值的子集和大于阈值的子集
				prob_low = float(len(sub_dataSet_1_1))/len(dataSet)                   #计算两个子集的占比
				prob_high = 1-prob_low
				sub_calc_low = self.CalcMethod(sub_dataSet_1_1)
				sub_calc_high = self.CalcMethod(sub_dataSet_2_2)
				new_calc_value = prob_low*sub_calc_low+prob_high*sub_calc_high
				# print(prob_low,prob_high,sub_calc_low,sub_calc_high,new_calc_value)
				if new_calc_value < calc_value:
					calc_value = new_calc_value
					best_index = i
					best_split_value = thld
					sub_dataSet_1 = sub_dataSet_1_1
					sub_dataSet_2 = sub_dataSet_2_2
		return best_index,best_split_value,sub_dataSet_1,sub_dataSet_2


# 根据某一属性值进行划分，返回划分后的数据集
	def SplitDataSet(self,dataSet,index,threshold):
		sub_dataSet_1 = list()
		sub_dataSet_2 = list()
		for item in dataSet:
			try:
				float(threshold)
				if item[index] <= threshold:
					sub_dataSet_1.append(item)
				else:
					sub_dataSet_2.append(item)
			except:
				if item[index] == threshold:
					sub_dataSet_1.append(item)
				else:
					sub_dataSet_2.append(item)
		return sub_dataSet_1,sub_dataSet_2

# 生成决策树， type表示采用哪种标准产生最优划分
	def GrowTree(self,dataSet,dec_tree):
		#若没有可用属性，结束算法
		if len(self.attr_indexs) == 0: 
			#此处计算此叶子节点的class,并存入决策树
			final_label = self.SelectClassLabel(dataSet)
			dec_tree['final'] = final_label
			return
		
		best_index,best_split_value,sub_dataSet_1,sub_dataSet_2 = self.SeletBestSplit(dataSet)

		# 预剪枝，将划分后子集大小小于5的划分剪去
		if self.prun_type == 'PREPRUN':
			if len(sub_dataSet_1)<=2 or len(sub_dataSet_2)<=2:
				final_label = self.SelectClassLabel(dataSet)
				dec_tree['final'] = final_label
				return 
		else:
			if len(sub_dataSet_1)==0 or len(sub_dataSet_2)==0:
				final_label = self.SelectClassLabel(dataSet)
				dec_tree['final'] = final_label
				return

		# 确定划分属性是数值型还是字符型
		try:
			float(best_split_value)
			split1 = 'low'
			split2 = 'high'
		except:
			split1 = 'yes'
			split2 = 'no'
		# 此处将划分属性加入决策树中
		key = str(best_index) + ',' + str(best_split_value)     #  key format : '0,2.4'
		dec_tree[key] = {}
		dec_tree[key][split1] = {}
		dec_tree[key][split2] = {}
		self.attr_indexs.remove(best_index)      #移除已用属性

		# 判断小于阈值的子集的class label是否一致
		is_same_class,same_label = self.IsAllinOneClass(sub_dataSet_1)
		# 如果所有元素label一致，将叶子节点的label存入决策树
		if is_same_class:
			dec_tree[key][split1]['final'] = same_label
		else:	
			self.GrowTree(sub_dataSet_1,dec_tree[key][split1])

		# 判断大于阈值的子集的class label是否一致
		is_same_class,same_label = self.IsAllinOneClass(sub_dataSet_2)
		if is_same_class:
			dec_tree[key][split2]['final'] = same_label
		else:
			self.GrowTree(sub_dataSet_2,dec_tree[key][split2])

# 是否所有数据都属于同一class
	def IsAllinOneClass(self,dataSet):
		class_list = [example[-1] for example in dataSet]
		if class_list.count(class_list[0]) == len(class_list):
			return True,class_list[0]
		return False,''

# 选择数据集中出现最多的class label最为此数据集的label
	def SelectClassLabel(self,dataSet):
		class_list = [example[-1] for example in dataSet]
		labels = set(class_list)
		major_class = ''
		major_class_len = 0
		for label in labels:
			if class_list.count(label) > major_class_len:
				major_class_len = class_list.count(label)
				major_class = label
		return major_class

	# 后剪枝
	def PostPrun(self,tree,dataSet):
		key = list(tree.keys())[0]
		if key == 'final':
			return

		attr_index = int(key.split(',')[0])
		attr_value = key.split(',')[1]
		sub_dataSet_1,sub_dataSet_2 = self.SplitDataSet(dataSet,attr_index,attr_value)

		self.PostPrun(tree[key]['low'],sub_dataSet_1)
		self.PostPrun(tree[key]['high'],sub_dataSet_2)
		old_corrate = self.ValidTree(dataSet,tree)
		label = self.SelectClassLabel(dataSet)
		new_corrate = self.ValidTree(dataSet,{'final':label})

		# 若剪枝后的决策树正确率高，就替换子树为叶子节点
		if new_corrate >= old_corrate:
			tree.update(final=tree.pop(key))
			tree['final'] = label
			return new_corrate
		return old_corrate



# 测试决策树，返回正确率
	def ValidTree(self,validSet,decision_tree):
		if len(validSet) == 0:
			return 0
		pos_count = 0     #正确的预测数
		for item in validSet:
			if self.ValidTransaction(decision_tree,item):
				pos_count += 1

		return float(pos_count)/len(validSet)

	def ValidTransaction(self,decision_tree,item):
		key = list(decision_tree.keys())[0]
		tree = decision_tree[key]
		while not key == 'final':
			attr_index = int(key.split(',')[0])
			attr_value = key.split(',')[1]
			try:
				float(attr_value)
				if item[attr_index] <= attr_value:
					key = list(tree['low'].keys())[0]
					tree = tree['low'][key]
				else:
					key = list(tree['high'].keys())[0]
					tree = tree['high'][key]
			except:
				if item[attr_index] == attr_value:
					key = list(tree['yes'].keys())[0]
					tree = tree['yes'][key]
				else:
					key = list(tree['no'].keys())[0]
					tree = tree['no'][key]	
		if tree == item[-1]:
			return True
		return False


	# 将数据集划分为part_num份
	def DivideDataSet(self,part_num):
		devide_trans = []                          #随机分成part_num份后的数据集
		trans_total = len(self.transactions) 	   #原始数据集的大小
		part_size = int(trans_total/10)            #数据子集的大小
		orig_trans = copy.copy(self.transactions)  #原始数据集的拷贝

		# 将原始数据集随机分成10份
		for i in range(part_num-1):
			part_trans = []
			for l in range(part_size):
				r = random.randint(0,trans_total-1)
				part_trans.append(orig_trans[r])
				orig_trans.remove(orig_trans[r])
				trans_total -= 1
			devide_trans.append(part_trans)
		devide_trans.append(orig_trans)
		return devide_trans


	def HoldOutMethod(self):
		train_trans = []
		valid_trans = []
		# 将数据集随机分为训练集和测试集
		for item in self.transactions:
			if random.randint(0,1):
				train_trans.append(item)
			else:
				valid_trans.append(item)
		# 采用3种划分方法，和3种剪枝策略，验证数据集
		for split_type in range(1,4):
			self.ChangeSplitMod(split_type)
			for prun_type in range(1,4):
				self.ChangePrunMod(prun_type)
				print('\n划分策略:'+self.split_type+',剪枝策略:'+self.prun_type)
				self.InitTree()
				self.GrowTree(train_trans,self.decision_tree)
				if self.prun_type == 'POSTPRUN':
					cor_percent = self.PostPrun(self.decision_tree,valid_trans)
				else:
					cor_percent = self.ValidTree(valid_trans,self.decision_tree)
				print(self.decision_tree)
				print(cor_percent)


	def CrossValidation(self):
		total_percent = 0.0
		devide_trans = self.DivideDataSet(10)              #随机分成10份后的数据集

		# 10次测试和检验
		# 采用3种划分方法，和3种剪枝策略，验证数据集
		for split_type in range(1,4):
			self.ChangeSplitMod(split_type)
			for prun_type in range(1,4):
				self.ChangePrunMod(prun_type)
				print('\n划分策略:'+self.split_type+',剪枝策略:'+self.prun_type)
				for i in range(10):
					valid_trans = devide_trans[i]
					train_trans = []
					for j in range(10):
						if not j == i:
							train_trans.extend(devide_trans[j])
					self.InitTree()
					self.GrowTree(train_trans,self.decision_tree)
					# print(self.decision_tree)
					total_percent += self.ValidTree(valid_trans,self.decision_tree)
					# print(total_percent/(i+1))
				ave_percent = total_percent/10
				print(ave_percent)
				total_percent = 0.0

	# def BootstrapValidation(self):

	def AdaBoost(self,times):
		total_size = len(self.transactions)
		ws = []  #权值列表
		# 初始化权值列表
		for i in range(total_size):
			ws.append(1/total_size)

		# 迭代times次
		for t in range(times):
			# 选取N个数据作为训练集
			train_set = []
			for n in range(total_size):
				rand_index = random.randint(0,total_size-1)
				train_set.append(self.transactions[rand_index])
			# 训练得到基础决策树
			self.InitTree()
			self.GrowTree(train_trans,self.decision_tree)
			index = 0
			err_total = 0
			cor_set = []
			err_set = []
			for item in self.transactions:
				if self.ValidTransaction(self.decision_tree,item):
					err_total += ws[index]
					cor_set.append(index)
				else:
					err_set.append(index)
				index += 1
			err_rate = err_total/total_size
			






if __name__ == "__main__":
	ms = MiningSolution("DataSet/seeds.txt")
	ms.HoldOutMethod()
	# ms.CrossValidation()


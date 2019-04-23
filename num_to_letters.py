dict_number = {'0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven','8':'eight','9':'nine','10':'ten','11':'eleven','12':'twelve','13':'thirteen','14':'fourteen','15':'fivteen','16':'sixteen',
			   '17':'seventeen','18':'eighteen','19':'ninteen','20':'twenty','30':'thirty','40':'fourty','50':'fifty','60':'sixty','70':'seventy','80':'eighty','90':'ninty'}
list_len = {2:'thousands',3:'million',4:'billion',5:'Cillion',6:'Dillion',7:'Eillion'}
number = input('put your num:   ')

def split_num(numStr):
	
	if '.' in numStr:
		num_list = numStr.split('.')
	elif ',' in numStr:
		num_list = numStr.split(',')
	else:
		num_list = [numStr]
	return num_list

	
def split_every_three_num(num_list):
	left_side = num_list[0][::-1]

	if len(left_side)%3 == 0:
		range_parameter = len(left_side)//3
	else:
		range_parameter =  len(left_side)//3 + 1
	spliting_list = []
	
	for i in range(range_parameter):
		index = left_side[3*i:3*i+3][::-1]
		spliting_list.append(index)
	return spliting_list

def read_nums(last_list):
	last_list = last_list[::-1]
	read_num_list = []
	
	for index in last_list:
		if index in dict_number:
			if index == '0':
				continue
			else:
				read_num = '{}'.format(dict_number[index])
				read_num_list.append(read_num)
				continue 
		
		else:
			if index == '00':
				continue
				
			elif index[0] == '0':
				if index[1] == '0':
					if index[2] == '0':
						continue 
					else:
						new_str_num = index[2:]
						read_num = '{}'.format(dict_number[new_str_num])
						read_num_list.append(read_num)
				else:
					new_str_num = index[1:]
					if new_str_num in dict_number:
						read_num = '{}'.format(dict_number[new_str_num])
						read_num_list.append(read_num)
					else:
						first_new_str_num=new_str_num[0]+'0'
						read_num = '{} {}'.format(dict_number[first_new_str_num],dict_number[new_str_num[1]])
						read_num_list.append(read_num)
						
			else:
				if index[1] == '0'and index[2] == '0':

					read_num = '{} hundred'.format(dict_number[index[0]])
					read_num_list.append(read_num)
				elif index[1] == '0':
					read_num = '{} hundred and {} '.format(dict_number[index[0]] ,dict_number[index[2]])
					read_num_list.append(read_num)
				else:
					new_str_num = index[1:]
					if new_str_num in dict_number:
						if len(index)==3:
							
							read_num = '{} hundred and {}'.format(dict_number[index[0]],dict_number[index[1]+index[2]])
							read_num_list.append(read_num)
						else:
							
							new_str_num = index[0]+'0'
							read_num = '{} {}'.format(dict_number[new_str_num],dict_number[index[-1]])
							read_num_list.append(read_num)
					else:
						first_new_str_num = new_str_num[0]+'0'
						read_num = '{} hundred and {} {}'.format(dict_number[index[0]],dict_number[first_new_str_num],dict_number[index[2]])
						read_num_list.append(read_num)						
	return read_num_list



def last_list():
	splitting_list = split_every_three_num([number])[::-1]
	read_num_list = read_nums(split_every_three_num(split_num(number)))
	print(splitting_list,'split num')
	print(read_num_list,"read_num")
	len_splitting_list = len(splitting_list)
	range_ = len_splitting_list
	print(range_)
	
	last_list_ = []
	for i in range(range_):
		last_list_.append(read_num_list[i])
		if splitting_list[i] == '000' or splitting_list[i] == '00' or splitting_list[i] == '0':
			print(splitting_list[i],i)
			last_list_.append(splitting_list[i])
		else:
			continue
	return last_list_
	
print(last_list())

#print(read_nums(split_every_three_num(split_num(number))))	
#def last_read_number(read_num_list):
#	first_list = split_every_three_num([number])[::-1]
#	len_list = len(first_list)
#	print(len_list)
#	print(first_list)
#	print(read_num_list)
	
#	final_read_number = ' '
	
#	for index in first_list : 
#		for read_num in read_num_list:  
#			if index == '000' or index == '00' or index == '0':
#				len_list = len_list-1
#				break
		            	
#			else:
#				if len_list == 1:
#					final_read_number += read_num + ' '		
#					break
#				else:
#					final_read_number += read_num + ' ' +list_len[len_list]
#					len_list = len_list-1
					
#	return final_read_number

#print(split_every_three_num(split_num(number)))
		
#if num == '000':
#print(";ljfg")
#len_list = len_list-1
#continue
#else:
#print('000')
#if len_list == 1:
#final_read_number += num + ' ' 
#else:
#final_read_number += num + ' ' + list_len[len_list] + ' '
#len_list = len_list-1
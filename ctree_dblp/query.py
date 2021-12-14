from django.http import Http404, HttpResponse, HttpResponseRedirect
import os.path
import simplejson
from urllib2 import Request, urlopen, quote
from BeautifulSoup import BeautifulSoup as Soup
import random
import hashlib
import xml.etree.ElementTree as ET
import json
from operator import *
import MySQLdb
import MySQLdb.cursors

rand_str = str(random.random()).encode('utf8')
google_id = hashlib.md5(rand_str).hexdigest()[:16]
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Cookie': 'GSP=ID=%s' % google_id}

class DB:
  conn = None
  def connect(self):
    # self.conn = MySQLdb.connect(host="localhost", user="root", passwd="vidim", db="ctree_eu", use_unicode=True, charset="utf8", cursorclass=MySQLdb.cursors.DictCursor)
    self.conn = MySQLdb.connect(host="localhost", port = 3306, user="root", passwd="vidim", db="dblp_behaviors", use_unicode=True, charset="utf8", cursorclass=MySQLdb.cursors.DictCursor)
  def query(self, sql):
    try:
      cursor = self.conn.cursor()
      cursor.execute(sql)
      self.conn.commit()
    except (AttributeError, MySQLdb.OperationalError):
      self.connect()
      cursor = self.conn.cursor()
      cursor.execute(sql)
      self.conn.commit()
    return cursor


def collecting_data(request):
	db = DB()
	if request.GET.get('behavior'):
		db.query('INSERT INTO system_usage (userIP, action, value) VALUES \
			("' + data_table + '", ' + session + ', "' + column+ '");')
	else:
		raise Http404
            
	return HttpResponse({"reslut":"finished"})


def collecting_search(info):
	db = DB()
	db.query('INSERT INTO system_usage (userIP, action, value, others) VALUES \
		("' + info[2] + '", "search", "' + info[0] + '", "' + info[1] + '");')
	

def check_searching(request):
	period = []
	if request.GET.get('researcher'):
		xml_url = request.GET.get('researcher')
		# http://dblp.uni-trier.de/pers/hd/m/Ma:Kwan=Liu
		# http://dblp.uni-trier.de/pers/xx/m/Ma:Kwan=Liu.xml 
		# http://dblp.uni-trier.de/pers/hd/s/Shneiderman:Ben
		# print "request", request
		# ori_url = ori_url.encode('utf8')
		# print "ori_url", ori_url
		
		#xml_url = ori_url.replace("/hd/", "/xx/")
		xml_url += ".xml"

		
		request = Request(xml_url, headers=HEADERS)
		try:
			response = urlopen(request)
			html = response.read()
			html = html.decode('utf8')
			soup = Soup(html)
			all_year = []
			author = soup.person.author.string
			# get all the published years
			
			for y in soup.findAll('year'):
				if y.string not in all_year:
					print('Adding year', y.string)
					all_year.append(y.string)
			# print all_year
			period = [all_year[-1], all_year[0], author]
		except Exception:
			period = [-1]

	else:
		raise Http404

	return_json = simplejson.dumps(period, indent=4, use_decimal=True)
	# with open("./ctree_dblp/media/data/research_graph.json", "wb") as json_file:
	# 	json_file.write(return_json)

	return HttpResponse(return_json)


def open_webpage(url):
	# print "-", url
	request = Request(url, headers=HEADERS)
	result = []
	try:
		response = urlopen(request)
		html = response.read()
		html = html.decode('utf8')
		# print html
		parsed_html = Soup(html)
		outside = parsed_html.body.find('div', attrs={'id':'completesearch-authors'})
		container = outside.find('div', attrs={'class':'body hide-body'})
		# print container
		# print container.findAll('ul')[0]
		# print container.findAll('ul')[0].findAll('li')
		for s in container.findAll('ul')[0].findAll('li'):
			# print "***", s
			link = s.find('a').get('href')
			name = u''.join(s.find('span').findAll(text=True)) #s.find('span').text
			# print link
			# print name
			if s.find('br'):
				extra = s.find('small').text
				result.append([name, link, extra])
			else:
				result.append([name, link])
		# result = [all_year[-1], all_year[0], author]
	except Exception:
		result = [-1]

	return result


def search_searching(request):
	result = []
	if request.GET.get('researcher'):
		ori_url = request.GET.get('researcher')
		new_url = ori_url.replace('/author', "")
		# http://dblp.uni-trier.de/pers/hd/m/Ma:Kwan=Liu
		# http://dblp.uni-trier.de/pers/xx/m/Ma:Kwan=Liu.xml 
		# http://dblp.uni-trier.de/pers/hd/s/Shneiderman:Ben
		# print "request", request
		# ori_url = ori_url.encode('utf8')
		# print "-", ori_url, "->", new_url
		result = open_webpage(ori_url)
		if result[0] == -1:
			result = open_webpage(new_url)
		# request = Request(ori_url, headers=HEADERS)

		# try:
		# 	response = urlopen(request)
		# 	html = response.read()
		# 	html = html.decode('utf8')
		# 	# print html
		# 	parsed_html = Soup(html)
		# 	outside = parsed_html.body.find('div', attrs={'id':'completesearch-authors'})
		# 	container = outside.find('div', attrs={'class':'body hide-body'})
		# 	# print container
		# 	# print container.findAll('ul')[0]
		# 	# print container.findAll('ul')[0].findAll('li')
		# 	for s in container.findAll('ul')[0].findAll('li'):
		# 		# print "***", s
		# 		link = s.find('a').get('href')
		# 		name = u''.join(s.find('span').findAll(text=True)) #s.find('span').text
		# 		print link
		# 		print name
		# 		if s.find('br'):
		# 			extra = s.find('small').text
		# 			result.append([name, link, extra])
		# 		else:
		# 			result.append([name, link])
		# 	# result = [all_year[-1], all_year[0], author]
		# except Exception:
		# 	result = [-1]

	else:
		raise Http404
	# print "*", result
	return_json = simplejson.dumps(result, indent=4, use_decimal=True)
	# with open("./ctree_dblp/media/data/research_graph.json", "wb") as json_file:
	# 	json_file.write(return_json)

	return HttpResponse(return_json)

def update_tree_structure(request):
	if request.GET.get('final_setting'): 
		final_setting = json.loads(request.GET.get('final_setting'))
		ori_url = final_setting[0]
		sy = final_setting[1]
		ey = final_setting[2]
		career_period = final_setting[3]
		setting_gap = final_setting[4]
		target = final_setting[5]
		user_ip = final_setting[6].replace('.','')

		print "in update tree structure"
		print final_setting
		print sy, ey, setting_gap, target

		xml_url = ori_url.replace("/hd/", "/xx/")
		xml_url += ".xml"

		request = Request(xml_url, headers=HEADERS)
		response = urlopen(request)
		html = response.read()
		html = html.decode('utf8')
		soup = Soup(html)
		author_name =  soup.person.findAll('author')
		author = []
		for n in author_name:
			author.append(n.string)
		display_author = soup.person.author.string
		coauthorship = dict()
		publication = dict()
		coauthorship[author[0]] = [1, int(sy), int(ey), [], 0]
		# with open("./ctree_dblp/data/dblp_test.json", "rb") as json_file:
		# 	retuen_structure = json.load(json_file)

		# print author
		# collecting_search([author[0], str(sy)+"-"+str(ey), user_ip]) !!!

		unique_author_list = []
		unique_paper_list = []
		for y in soup.findAll('r'):
			co_author_list = []
			p_title = y.title.string
			p_year = y.year.string
			# print p_title
			if p_title == None:
				new_title = u''.join(y.find('title').findAll(text=True)) #s.find('span').text
				p_title = new_title
				
			if int(p_year) <= ey and int(p_year) >= sy:
				unique_paper_list.append(p_title)
			# if int(p_year) > ey or int(p_year) < sy:
			# 	continue
			paper_type = str(y.contents[0]).split('key="')[1].split("/")[0]
			for a in y.findAll('author'):
				co_author_list.append(a.string)
				if len(y.findAll('author')) == 1:
					coauthorship[author[0]][0] += 1 
					coauthorship[author[0]][3].append(p_title)
					if paper_type == "journals":
						coauthorship[author[0]][4] += 1
				if a.string not in author and a.string not in coauthorship:
					coauthorship[a.string] = [1, int(p_year), int(p_year), [p_title], 0]
					if int(p_year) <= ey and int(p_year) >= sy:
						unique_author_list.append(a.string)
					if paper_type == "journals":
						coauthorship[a.string][4] += 1
				elif a.string not in author:
					coauthorship[a.string][0] += 1
					coauthorship[a.string][3].append(p_title)
					if int(p_year) < coauthorship[a.string][1]:
						coauthorship[a.string][1] = int(p_year)
					elif int(p_year) > coauthorship[a.string][2]:
						coauthorship[a.string][2] = int(p_year)
					if paper_type == "journals":
						coauthorship[a.string][4] += 1

			if len(co_author_list) == 0:
				for a in y.findAll('editor'):
					co_author_list.append(a.string)
					if len(y.findAll('editor')) == 1:
						coauthorship[author[0]][0] += 1 
						coauthorship[author[0]][3].append(p_title)
						if paper_type == "journals":
							coauthorship[author[0]][4] += 1
					if a.string not in author and a.string not in coauthorship:
						coauthorship[a.string] = [1, int(p_year), int(p_year), [p_title], 0]
						if int(p_year) <= ey and int(p_year) >= sy:
							unique_author_list.append(a.string)
							if paper_type == "journals":
								coauthorship[a.string][4] += 1
					elif a.string not in author:
						coauthorship[a.string][0] += 1
						coauthorship[a.string][3].append(p_title)
						if int(p_year) < coauthorship[a.string][1]:
							coauthorship[a.string][1] = int(p_year)
						elif int(p_year) > coauthorship[a.string][2]:
							coauthorship[a.string][2] = int(p_year)
						if paper_type == "journals":
							coauthorship[a.string][4] += 1
			if y.pages:
				page_info = str(y.pages.string).split("-")
				if len(page_info) > 1:
					try:
						pages = int(page_info[1]) - int(page_info[0]) + 1
					except:
						pages = 1
				else:
					pages = 1
			else:
				pages = 1

			for a in author:
				try:
					author_order = co_author_list.index(a) + 1
					break
				except ValueError:
					continue

			# author_order = co_author_list.index(author) + 1

			if p_title not in publication:
				publication[p_title] = dict()
				publication[p_title]["coauthor"] = co_author_list
				publication[p_title]["author_count"] = len(co_author_list)-1
				publication[p_title]["author_order"] = int(author_order)
				publication[p_title]["year"] = int(p_year)
				publication[p_title]["type"] = paper_type
				publication[p_title]["pages"] = int(pages)
			else:
				p_title = p_title + " (" + paper_type + ")"
				# print "<<<", p_title
				publication[p_title] = dict()
				publication[p_title]["coauthor"] = co_author_list
				publication[p_title]["author_count"] = len(co_author_list)-1
				publication[p_title]["author_order"] = int(author_order)
				publication[p_title]["year"] = int(p_year)
				publication[p_title]["type"] = paper_type
				publication[p_title]["pages"] = int(pages)
	    # sys.exit()
		tree_egos, branches = tree_mapping(career_period, publication, coauthorship, author, sy, ey, setting_gap)
		
		one_tree = tree_structure(tree_egos[target], branches)

		for layer in one_tree['right']:
			layer['level']['down'] = sorted(layer['level']['down'], key=lambda k: k['sorting'])
			layer['level']['up'] = sorted(layer['level']['up'], key=lambda k: k['sorting'])
		for layer in one_tree['left']:
			layer['level']['down'] = sorted(layer['level']['down'], key=lambda k: k['sorting'])
			layer['level']['up'] = sorted(layer['level']['up'], key=lambda k: k['sorting'])

	else:
		raise Http404

	return_json = simplejson.dumps([one_tree, target], indent=4, use_decimal=True)

	return HttpResponse(return_json)


def get_tree_structure(request):
	if request.GET.get('final_setting'): 
		final_setting = json.loads(request.GET.get('final_setting'))
		ori_url = final_setting[0]
		sy = final_setting[1]
		ey = final_setting[2]
		career_period = final_setting[3]
		user_ip = final_setting[4].replace('.','')
		# http://dblp.uni-trier.de/pers/hd/m/Ma:Kwan=Liu
    	# http://dblp.uni-trier.de/pers/xx/m/Ma:Kwan=Liu.xml 
    	# http://dblp.uni-trier.de/pers/hd/s/Shneiderman:Ben
		xml_url = ori_url.replace("/hd/", "/xx/")
		xml_url += ".xml"

		request = Request(xml_url, headers=HEADERS)
		response = urlopen(request)
		html = response.read()
		html = html.decode('utf8')
		soup = Soup(html)
		author_name =  soup.person.findAll('author')
		author = []
		for n in author_name:
			author.append(n.string)
		display_author = soup.person.author.string
		coauthorship = dict()
		publication = dict()
		coauthorship[author[0]] = [1, int(sy), int(ey), [], 0]
		# with open("./ctree_dblp/data/dblp_test.json", "rb") as json_file:
		# 	retuen_structure = json.load(json_file)

		# print author
		# collecting_search([author[0], str(sy)+"-"+str(ey), user_ip]) !!!

		unique_author_list = []
		unique_paper_list = []
		graph = {}
		for y in soup.findAll('r'):
			co_author_list = []
			p_title = y.title.string
			p_year = y.year.string
			# print p_title
			if p_title == None:
				new_title = u''.join(y.find('title').findAll(text=True)) #s.find('span').text
				p_title = new_title
				
			if int(p_year) <= ey and int(p_year) >= sy:
				unique_paper_list.append(p_title)
			# if int(p_year) > ey or int(p_year) < sy:
			# 	continue
			paper_type = str(y.contents[0]).split('key="')[1].split("/")[0]
			for a in y.findAll('author'):
				co_author_list.append(a.string)
				if len(y.findAll('author')) == 1:
					coauthorship[author[0]][0] += 1 
					coauthorship[author[0]][3].append(p_title)
					if paper_type == "journals":
						coauthorship[author[0]][4] += 1
				if a.string not in author and a.string not in coauthorship:
					coauthorship[a.string] = [1, int(p_year), int(p_year), [p_title], 0]
					if int(p_year) <= ey and int(p_year) >= sy:
						unique_author_list.append(a.string)
					if paper_type == "journals":
						coauthorship[a.string][4] += 1
				elif a.string not in author:
					coauthorship[a.string][0] += 1
					coauthorship[a.string][3].append(p_title)
					if int(p_year) < coauthorship[a.string][1]:
						coauthorship[a.string][1] = int(p_year)
					elif int(p_year) > coauthorship[a.string][2]:
						coauthorship[a.string][2] = int(p_year)
					if paper_type == "journals":
						coauthorship[a.string][4] += 1

			if len(co_author_list) == 0:
				for a in y.findAll('editor'):
					co_author_list.append(a.string)
					if len(y.findAll('editor')) == 1:
						coauthorship[author[0]][0] += 1 
						coauthorship[author[0]][3].append(p_title)
						if paper_type == "journals":
							coauthorship[author[0]][4] += 1
					if a.string not in author and a.string not in coauthorship:
						coauthorship[a.string] = [1, int(p_year), int(p_year), [p_title], 0]
						if int(p_year) <= ey and int(p_year) >= sy:
							unique_author_list.append(a.string)
							if paper_type == "journals":
								coauthorship[a.string][4] += 1
					elif a.string not in author:
						coauthorship[a.string][0] += 1
						coauthorship[a.string][3].append(p_title)
						if int(p_year) < coauthorship[a.string][1]:
							coauthorship[a.string][1] = int(p_year)
						elif int(p_year) > coauthorship[a.string][2]:
							coauthorship[a.string][2] = int(p_year)
						if paper_type == "journals":
							coauthorship[a.string][4] += 1
			if y.pages:
				page_info = str(y.pages.string).split("-")
				if len(page_info) > 1:
					try:
						pages = int(page_info[1]) - int(page_info[0]) + 1
					except:
						pages = 1
				else:
					pages = 1
			else:
				pages = 1

			for a in author:
				try:
					author_order = co_author_list.index(a) + 1
					break
				except ValueError:
					continue

			# author_order = co_author_list.index(author) + 1

			if p_title not in publication:
				publication[p_title] = dict()
				publication[p_title]["coauthor"] = co_author_list
				publication[p_title]["author_count"] = len(co_author_list)-1
				publication[p_title]["author_order"] = int(author_order)
				publication[p_title]["year"] = int(p_year)
				publication[p_title]["type"] = paper_type
				publication[p_title]["pages"] = int(pages)
			else:
				p_title = p_title + " (" + paper_type + ")"
				# print "<<<", p_title
				publication[p_title] = dict()
				publication[p_title]["coauthor"] = co_author_list
				publication[p_title]["author_count"] = len(co_author_list)-1
				publication[p_title]["author_order"] = int(author_order)
				publication[p_title]["year"] = int(p_year)
				publication[p_title]["type"] = paper_type
				publication[p_title]["pages"] = int(pages)
	    # sys.exit()
		tree_egos, branches, legends, final_info_table = tree_mapping(career_period, publication, coauthorship, author, sy, ey)
		graph = graph_mapping(career_period, publication, coauthorship, author, sy, ey, user_ip)
		final_structure = dict()
		final_structure["all"] = dict()
		
		for one_ego in tree_egos:
			# print one_ego
			one_tree = tree_structure(tree_egos[one_ego], branches)
			final_structure["all"][one_ego] = one_tree

		# sort sticks
		for d in final_structure:
		    for e in final_structure[d]:
		        # print final_structure[d][e]
		        for layer in final_structure[d][e]['right']:
		            layer['level']['down'] = sorted(layer['level']['down'], key=lambda k: k['sorting'])
		            layer['level']['up'] = sorted(layer['level']['up'], key=lambda k: k['sorting'])
		        for layer in final_structure[d][e]['left']:
		            layer['level']['down'] = sorted(layer['level']['down'], key=lambda k: k['sorting'])
		            layer['level']['up'] = sorted(layer['level']['up'], key=lambda k: k['sorting'])
			

	else:
		raise Http404

	
	final_unique_author_list = ["None"] + sorted(unique_author_list)
	final_unique_paper_list = ["None"] + sorted(unique_paper_list)
	# print final_unique_author_list
	# print final_unique_paper_list
	final_return = [final_structure, final_unique_author_list, final_unique_paper_list, legends, final_info_table, graph]
	return_json = simplejson.dumps(final_return, indent=4, use_decimal=True)

	return HttpResponse(return_json)


def tree_mapping(career_period, publication, coauthors, ego, sy, ey, setting_gap = None):
	tree_egos = dict()
	tree_egos["tree1"] = []
	tree_egos["tree2"] = []
	tree_egos["tree3"] = []
	tree_egos["tree4"] = []

	tree_info = dict()
	tree_info["paper_tree"] = {}
	tree_info["author_tree"] = {}
	tree_info["unique_author_tree"] = {}

	period = ey - sy + 1
	# gap = 1
	year_gap = []
	color_gap = []
	# branch_layer = period
	if period <= 10:
		gap = 1
	elif 10 < period <= 20:
		gap = 2
	elif 20 < period <= 30:
		gap = 3
	elif 30 < period <= 40:
		gap = 4
	elif 40 < period <= 50:
		gap = 5
	else:
		gap = 6

	if setting_gap:
		gap = int(setting_gap)

	start =  int(career_period[0])
	end = int(career_period[1])
	t_gap = int(career_period[2])
	
	for x in range(start+t_gap, end+1, t_gap):
		# print x
		color_gap.append(int(x))

	for y in range(sy+gap, ey+1, gap):
		year_gap.append(int(y))

	if not year_gap:
		year_gap.append(start)
		color_gap.append(start)

	print "*****", ego[0], "*****"
	print "Gap: ", gap, " Year_gap: ", year_gap, "Color_gap: ", color_gap
	branch_layer = len(year_gap) + 1
	# color_gap = year_gap
    # sys.exit()
    # ["stick", "leaf", "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit"]
	for paper in publication:
		if publication[paper]["year"] > ey or publication[paper]["year"] < sy:
				continue

		tree_info["paper_tree"][paper] = {"Published year": publication[paper]["year"], "Paper type": publication[paper]["type"], "Author order": publication[paper]["author_order"], "Leaves": []}
		# tree_info["tree2"][paper] = {"Published year": publication[paper]["year"], "Paper type": publication[paper]["type"], "Author order": publication[paper]["author_order"], "Leaves": []}
		# solo paper
		if publication[paper]["author_count"] == 0:
			# print paper
			# print "in solo publication"
			first_real_year = 0
			paper_real_year = int(publication[paper]["year"]) - sy
			data1 = [paper, ego[0], "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit", ego[0], first_real_year, paper_real_year]
			data2 = [paper, ego[0], "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit", ego[0], first_real_year, paper_real_year]
			
			tree_info["paper_tree"][paper]["Leaves"].append(ego[0]);
			# trunk			
			data1[4] = 0
			data2[2] = 0
			# branch as year
			if len(year_gap) > 1:
				if publication[paper]["year"] < year_gap[0]:
					data1[3] = 0
					data2[3] = 0
				elif publication[paper]["year"] >= year_gap[-1]:
					data1[3] = len(year_gap)
					data2[3] = len(year_gap)
				else:
					for g in range(len(year_gap)-1):
						if year_gap[g] <= publication[paper]["year"] < year_gap[g+1]:
							data1[3] = g+1
							data2[3] = g+1
			else:
				data1[3] = 0
				data2[3] = 0
			# branch as author order
			# branch side
			if publication[paper]["type"] == "conf":
				# print publication[paper]["type"]
				data1[2] = 0
				data2[4] = 0
			else:
				data1[2] = 1
				data2[4] = 1

			data1[5] = 1 # leaf color for solo paper
			data1[6] = 0 # leaf size for solo paper
	
			data2[5] = 1 # leaf color for solo paper
			data2[6] = 0 # leaf size for solo paper

			p_length = int(publication[paper]["pages"])
			
			if p_length == 1:
				data1[7] = 0 # fruit
			elif 1 < p_length <= 4:
				data1[7] = 0 # fruit
			elif 4 < p_length <= 8:
				data1[7] = 2 # fruit
			elif 8 < p_length <= 12:
				data1[7] = 3 # fruit
			elif 12 < p_length:
				data1[7] = 4 # fruit

			data2[7] = 0
			
			tree_egos["tree1"].append(data1)
			tree_egos["tree2"].append(data2)
			
			continue

		# general paper
		# print paper
		coauthor_order = 1
		for author in publication[paper]["coauthor"]:
			if author in ego:
				tree_info["paper_tree"][paper]["Leaves"].append(ego[0]);
				coauthor_order += 1
				continue
			tree_info["paper_tree"][paper]["Leaves"].append(author);

			first_real_year = int(coauthors[author][1]) - sy
			paper_real_year = int(publication[paper]["year"]) - sy
			data1 = [paper, ego[0], "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit", author, first_real_year, paper_real_year] # stick, leaf
			data2 = [paper, ego[0], "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit", author, first_real_year, paper_real_year]
			
			# trunk
			if publication[paper]["author_order"] > 1:
				data1[4] = 1
				data2[2] = 1
			else:
				data1[4] = 0
				data2[2] = 0

			# branch as year
			if len(year_gap) > 1:
				if publication[paper]["year"] < year_gap[0]:
					data1[3] = 0
					data2[3] = 0
				elif publication[paper]["year"] >= year_gap[-1]:
					data1[3] = len(year_gap)
					data2[3] = len(year_gap)
				else:
					for g in range(len(year_gap)-1):
						if year_gap[g] <= publication[paper]["year"] < year_gap[g+1]:
							data1[3] = g+1
							data2[3] = g+1
			else:
				data1[3] = 0
				data2[3] = 0

			# branch side
			if publication[paper]["type"] == "conf":
				# print publication[paper]["type"]
				data1[2] = 0
				data2[4] = 0
			else:
				data1[2] = 1
				# data5[7] = 0 # fruit
				# data6[2] = 1
				data2[4] = 1

			total_collaborate_paper = coauthors[author][0]
			first_collaborated = coauthors[author][1]
			co_period = coauthors[author][2] - coauthors[author][1] + 1
			
			if len(color_gap) > 1:
				if first_collaborated < color_gap[0]:
					data1[5] = 0
					data2[5] = 0
				elif first_collaborated >= color_gap[-1]:
					data1[5] = len(color_gap)
					data2[5] = len(color_gap)
				else:
					for g in range(len(color_gap)-1):
						if color_gap[g] <= first_collaborated < color_gap[g+1]:
							data1[5] = g+1
							data2[5] = g+1
			else:
				data1[5] = 0
				data2[5] = 0

			if len(color_gap) <= 6:
				data1[5] += 2
				data2[5] += 2
			
			if total_collaborate_paper == 1:
				data1[6] = 1 # leaf size
			elif 1 < total_collaborate_paper <= 3:
				data1[6] = 2 # leaf size
			elif 3 < total_collaborate_paper <= 5:
				data1[6] = 3 # leaf size
			elif 5 < total_collaborate_paper <= 10:
				data1[6] = 4 # leaf size
			elif 10 < total_collaborate_paper <= 20:
				data1[6] = 5 # leaf size
			elif 20 < total_collaborate_paper:
				data1[6] = 6 # leaf size

			data2[6] = co_period/t_gap + 1 # leaf size
			if data2[6] > 6:
				data2[6] = 6


			p_length = int(publication[paper]["pages"])
			
			if p_length == 1:
				data1[7] = 0 # fruit
			elif 1 < p_length < 4:
				data1[7] = 0 # fruit
			elif 4 <= p_length <= 8:
				data1[7] = 2 # fruit
			elif 8 < p_length <= 12:
				data1[7] = 3 # fruit
			elif 12 < p_length:
				data1[7] = 4 # fruit

			# data6[7] = 0 # fruit
			data2[7] = 0 # fruit

			tree_egos["tree1"].append(data1)
			tree_egos["tree2"].append(data2)
			
			coauthor_order += 1

	for coauthor in coauthors:
		# solo paper
		fruit_val = 0
		
		# data3 = [coauthor, ego[0], "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit", "leafid"]
		# data4 = [coauthor, ego[0], "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit", "leafid"]
		data3_stick = [coauthor, ego[0], "trunk", "branch", "b_side"]
		data4_stick = [coauthor, ego[0], "trunk", "branch", "b_side"]

		tree_info["unique_author_tree"][coauthor] = {"Total collaboration": coauthors[coauthor][0], "First collaboration": coauthors[coauthor][1], "Leaves": []}
		
		# trunk: one-time co-authorship
		if coauthors[coauthor][0] == 1:
			data4_stick[2] = 1
			data3_stick[4] = 0
			data4_stick[4] = random.randint(0, 1)
		else:
			data4_stick[2] = 0
			data3_stick[4] = 1
			if coauthors[coauthor][0] > 3:
				data4_stick[4] = 1
			else:
				data4_stick[4] = 0


        # branch as first time coauthored
		if len(year_gap) > 1:
			if coauthors[coauthor][1] < year_gap[0]:
				data3_stick[3] = 0
				data4_stick[3] = 0
			elif coauthors[coauthor][1] >= year_gap[-1]:
				data3_stick[3] = len(year_gap)
				data4_stick[3] = len(year_gap)
			else:
				for g in range(len(year_gap)-1):
					if year_gap[g] <= coauthors[coauthor][1] < year_gap[g+1]:
						data3_stick[3] = g+1
						data4_stick[3] = g+1
		else:
			data3_stick[3] = 0
			data4_stick[3] = 0

		co_period = coauthors[coauthor][2] - coauthors[coauthor][1]
		jour_cnt = coauthors[coauthor][4]

		if co_period+1 > t_gap:
			data3_stick[2] = 1
		else:
			data3_stick[2] = 0

		if co_period > 6:
			co_period = 6 # fruit
		if jour_cnt > 6:
			jour_cnt = 6 # fruit
		# co_frequency = float(coauthors[coauthor][0]) / float(co_period)
		# fruit_val = co_period # fruit

		# first_real_year = int(coauthors[coauthor][1]) - sy
		for paper in coauthors[coauthor][3]:
			if publication[paper]["year"] > ey or publication[paper]["year"] < sy:
				continue
			
			published_time = publication[paper]["year"]
			# if len(year_gap) > 1:
			# 	if published_time < year_gap[0]:
			# 		data3_stick[3] = 0
			# 		cat_time = [sy, year_gap[0]]
			# 		if coauthor+"0" not in tree_info["author_tree"]:
			# 			tree_info["author_tree"][coauthor+"0"] = {"Co-authored paper count": coauthors[coauthor][0], "First co-authored year": coauthors[coauthor][1], "Leaves": []}
			# 		tree_info["author_tree"][coauthor+"0"]["Leaves"].append(paper+' (' +  str(published_time) + ')')
			# 	elif published_time >= year_gap[-1]:
			# 		data3_stick[3] = len(year_gap)
			# 		cat_time = [year_gap[-1], ey+1]
			# 		if coauthor+str(len(year_gap)) not in tree_info["author_tree"]:
			# 			tree_info["author_tree"][coauthor+str(len(year_gap))] = {"Co-authored paper count": coauthors[coauthor][0], "First co-authored year": coauthors[coauthor][1], "Leaves": []}
			# 		tree_info["author_tree"][coauthor+str(len(year_gap))]["Leaves"].append(paper +' (' +  str(published_time) + ')')
			# 	else:
			# 		for g in range(len(year_gap)-1):
			# 			if year_gap[g] <= published_time < year_gap[g+1]:
			# 				data3_stick[3] = g+1
			# 				cat_time = [year_gap[g], year_gap[g+1]]
			# 				if coauthor+str(g+1) not in tree_info["author_tree"]:
			# 					tree_info["author_tree"][coauthor+str(g+1)] = {"Co-authored paper count": coauthors[coauthor][0], "First co-authored year": coauthors[coauthor][1], "Leaves": []}
			# 				tree_info["author_tree"][coauthor+str(g+1)]["Leaves"].append(paper+' (' + str(published_time) + ')')
			# 				break

			# 	if cat_time[0] <= coauthors[coauthor][1] < cat_time[1]:
			# 		data3_stick[2] = 0
			# 	else:
			# 		data3_stick[2] = 1
			# else:
			# 	data3_stick[3] = 0
			# 	data3_stick[2] = 0
			tree_info["unique_author_tree"][coauthor]["Leaves"].append(paper+' (' +  str(published_time) + ')')

			data3 = data3_stick + ["leaf_color", "leaf_size"] + [jour_cnt, paper, paper_real_year, first_real_year]
			data4 = data4_stick + ["leaf_color", "leaf_size", co_period, paper, paper_real_year, first_real_year]

			# leaf color
			if publication[paper]["type"] == "journals": # "conf":
				data4[5] = 4
			elif publication[paper]["type"] == "conf":
				data4[5] = 6
			else:
				data4[5] = 0

			# co-author order
			# order = publication[paper]["author_order"]			

			total_author = len(publication[paper]["coauthor"])
			if total_author > 5:
				data3[6] = 5
				# data4[6] = 5
			else:
				data3[6] = total_author
				# data4[6] = total_author			
			
			p_length = int(publication[paper]["pages"])
			if p_length < 5:
				data4[6] = 1
			if 5 <= p_length < 8:
				data4[6] = 2
			else:
				data4[6] = 3
			
			
			# leaf color
			if len(color_gap) > 1:
				if publication[paper]["year"] < color_gap[0]:
					data3[5] = 0
					# data4[6] = len(color_gap)
				elif publication[paper]["year"] >= color_gap[-1]:
					data3[5] = len(color_gap) 
					# data4[6] = 0
				else:
					for g in range(len(color_gap)-1):
						if color_gap[g] <= publication[paper]["year"] < color_gap[g+1]:
							data3[5] = g+1
							# data4[6] = len(color_gap)-g-1
			else:
				data3[5] = 0
			if len(color_gap) <= 6:
				data3[5] += 2
			
			tree_egos["tree3"].append(data3)
			tree_egos["tree4"].append(data4)
			
	if setting_gap:
		return tree_egos, branch_layer

	return tree_egos, branch_layer, color_gap, tree_info


def tree_structure(tree_ego, branch_layer):
	structure = dict()
	egoid_index = -1
	alterid_index = 0
	# leafid_index = 1
	trunk_index = 2
	branch_index = 3
	bside_index = 4
	leaf_color_index = 5
	leaf_size_index = 6
	fruit_size_index = 7

	sorting_index = 10
	leafid_index = 8
	order_index = 9

	# branch_layer = 10
	stick = alterid_index
	

	# print stick_unique
	structure["right"] = []
	structure["left"] = []

	alter_array_right_up = []
	alter_array_left_up = []
	alter_array_right_down = []
	alter_array_left_down = []

	for total in range(branch_layer):
		structure["right"].append({"level": {"up": [], "down": []}})
		structure["left"].append({"level": {"up": [], "down": []}})
		alter_array_right_up.append([])
		alter_array_left_up.append([])
		alter_array_right_down.append([])
		alter_array_left_down.append([])

	# for tree in tree_egos:
	# ["stick", "leaf", "trunk", "branch", "b_side", "leaf_color", "leaf_size", "fruit"]
	for meeting in tree_ego:
		# print "********"
		# print meeting
		# left
		if meeting[trunk_index] == 0:
			level = 0
			new_alter = -1
			for l in range(branch_layer):
				# level and up
				if meeting[branch_index] == l and meeting[bside_index] == 1:
					if len(alter_array_left_up[level]) == 0:
						structure["left"][level]["level"]["up"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index],  "sorting": meeting[sorting_index], "leaf": []})
						structure["left"][level]["level"]["up"][len(alter_array_left_up[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]}) 
						alter_array_left_up[level].append(meeting[stick])

					else:
						count_alter = 0
						for a in alter_array_left_up[level]:
							if meeting[stick] == a:
								new_alter = count_alter
								break
							count_alter += 1
						if new_alter == -1:
							structure["left"][level]["level"]["up"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
							structure["left"][level]["level"]["up"][len(alter_array_left_up[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
							alter_array_left_up[level].append(meeting[stick])
						else:
							structure["left"][level]["level"]["up"][new_alter]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
					break

				# level and down
				elif meeting[branch_index] == l and meeting[bside_index] == 0:
					if len(alter_array_left_down[level]) == 0:
						structure["left"][level]["level"]["down"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
						structure["left"][level]["level"]["down"][len(alter_array_left_down[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
						alter_array_left_down[level].append(meeting[stick])
					else:
						count_alter = 0
						for a in alter_array_left_down[level]:
							if meeting[stick] == a:
								new_alter = count_alter
								break
							count_alter += 1
						if new_alter == -1:
							structure["left"][level]["level"]["down"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
							structure["left"][level]["level"]["down"][len(alter_array_left_down[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
							alter_array_left_down[level].append(meeting[stick])
						else:
							structure["left"][level]["level"]["down"][new_alter]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
					break
				level += 1
		# right
		else:
			level = 0
			new_alter = -1
			for l in range(branch_layer):
				# level and up
				if meeting[branch_index] == l and meeting[bside_index] == 1:
					if len(alter_array_right_up[level]) == 0:
						structure["right"][level]["level"]["up"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
						structure["right"][level]["level"]["up"][len(alter_array_right_up[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
						alter_array_right_up[level].append(meeting[stick])
					else:
						count_alter = 0
						for a in alter_array_right_up[level]:
							if meeting[stick] == a:
								new_alter = count_alter
								break
							count_alter += 1
						if new_alter == -1:
							structure["right"][level]["level"]["up"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
							structure["right"][level]["level"]["up"][len(alter_array_right_up[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
							alter_array_right_up[level].append(meeting[stick])
						else:
							structure["right"][level]["level"]["up"][new_alter]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
					break
				# level and down
				elif meeting[branch_index] == l and meeting[bside_index] == 0:
					if len(alter_array_right_down[level]) == 0:
						structure["right"][level]["level"]["down"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
						structure["right"][level]["level"]["down"][len(alter_array_right_down[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
						alter_array_right_down[level].append(meeting[stick])
					else:
						count_alter = 0
						for a in alter_array_right_down[level]:
							if meeting[stick] == a:
								new_alter = count_alter
								break
							count_alter += 1
						if new_alter == -1:
							structure["right"][level]["level"]["down"].append({"id": meeting[stick], "fruit": meeting[fruit_size_index], "sorting": meeting[sorting_index], "leaf": []})
							structure["right"][level]["level"]["down"][len(alter_array_right_down[level])]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
							alter_array_right_down[level].append(meeting[stick])
						else:
							structure["right"][level]["level"]["down"][new_alter]["leaf"].append({"size": meeting[leaf_size_index], "color": meeting[leaf_color_index], "leaf_id": meeting[leafid_index], "order": meeting[order_index]})
					break
				level += 1

	return structure



color_cat = ["#ffffff","#e39ac5","#b04d84","#821b54"] # conf, others, jour 
def graph_mapping(career_period, publication, coauthors, ego, sy, ey, user_ip):
	graph_egos = dict()
	graph_egos["tree1"] = {'nodes': [], 'links': []}
	graph_egos["tree2"] = {'nodes': [], 'links': []}
	graph_egos["tree3"] = {'nodes': [], 'links': []}
	graph_egos["tree4"] = {'nodes': [], 'links': []}
	period = ey - sy + 1
	paper_node_idx = []
	author_node_idx = []

	color_gap = []
	start =  int(career_period[0])
	end = int(career_period[1])
	t_gap = int(career_period[2])
	
	for x in range(start+t_gap, end, t_gap):
		# print x
		color_gap.append(int(x))

	if not color_gap:
		color_gap.append(start)
	
	graph_egos["tree1"]['nodes'].append({"type": "diamond", "size": 5, "group": 0, "label": ego[0]})
	# graph_egos["tree2"]['nodes'].append({"type": "diamond", "size": 5, "group": 0, "label": ego[0]})
	paper_node_idx.append(ego[0])
	matrix_data = {'pub':{}, 'coau':{}}
	matrix_data['coau'][ego[0]] = coauthors[ego[0]]
	total_pub = 0;
	for paper in publication:
		total_pub += 1
		if publication[paper]["year"] > ey or publication[paper]["year"] < sy:
				continue
		matrix_data['pub'][paper] = publication[paper]

		paper_node_idx.append(paper)
		paper_color = 1
		
		if publication[paper]["type"] == 'conf':
			graph_egos["tree1"]['nodes'].append({"type": "square", "size": publication[paper]["pages"], "group": 1, "label": paper})
			# graph_egos["tree2"]['nodes'].append({"type": "square", "size": len(publication[paper]["coauthor"]), "group": 1, "label": paper})
		elif publication[paper]["type"] == 'journals':
			paper_color = 3
			graph_egos["tree1"]['nodes'].append({"type": "square", "size": publication[paper]["pages"], "group": 3, "label": paper})
			# graph_egos["tree2"]['nodes'].append({"type": "square", "size": len(publication[paper]["coauthor"]), "group": 3, "label": paper})
		else:
			paper_color = 2
			graph_egos["tree1"]['nodes'].append({"type": "square", "size": publication[paper]["pages"], "group": 2, "label": paper})
			# graph_egos["tree2"]['nodes'].append({"type": "square", "size": len(publication[paper]["coauthor"]), "group": 2, "label": paper})
		
		if publication[paper]["author_count"] == 0:
			graph_egos["tree1"]['links'].append({"source": 0, "target": paper_node_idx.index(paper), "value": "#f45e00"})
			# graph_egos["tree2"]['links'].append({"source": 0, "target": paper_node_idx.index(paper), "value": "#f45e00"})
			continue
		if publication[paper]["author_order"] > 1:
			graph_egos["tree1"]['links'].append({"source": 0, "target": paper_node_idx.index(paper), "value": "Gray"})
			# graph_egos["tree2"]['links'].append({"source": 0, "target": paper_node_idx.index(paper), "value": "Gray"})
		else:
			graph_egos["tree1"]['links'].append({"source": 0, "target": paper_node_idx.index(paper), "value": "#f45e00"})
			# graph_egos["tree2"]['links'].append({"source": 0, "target": paper_node_idx.index(paper), "value": "#f45e00"})
			
		coauthor_order = 1
		for author in publication[paper]["coauthor"]:
			if author in ego:
				coauthor_order += 1
				continue
			
			if author not in paper_node_idx:
				paper_node_idx.append(author)

				first_collaborated = coauthors[author][1]
				matrix_data['coau'][author] = coauthors[author]

				if first_collaborated < color_gap[0]:
					au_group = 0
					au_group = 0
				elif first_collaborated >= color_gap[-1]:
					au_group = len(color_gap)
					au_group = len(color_gap)
				else:
					for g in range(len(color_gap)-1):
						if color_gap[g] <= first_collaborated < color_gap[g+1]:
							au_group = g+1
							au_group = g+1

				if len(color_gap) <= 6:
					au_group += 2
				graph_egos["tree1"]['nodes'].append({"type": "circle", "size": coauthors[author][0], "group": au_group + 4, "label": author})
				# graph_egos["tree2"]['nodes'].append({"type": "circle", "size": coauthors[author][0], "group": au_group + 4, "label": author})

			graph_egos["tree1"]['links'].append({"source": paper_node_idx.index(paper), "target": paper_node_idx.index(author), "value": color_cat[paper_color]})
			# graph_egos["tree2"]['links'].append({"source": paper_node_idx.index(paper), "target": paper_node_idx.index(author), "value": color_cat[paper_color]})

	# graph_egos["tree1"]['nodes'][0]["size"] = total_pub
	# graph_egos["tree2"]['nodes'][0]["size"] = total_pub
	
	return graph_egos
	# return_json = simplejson.dumps(graph_egos, indent=4, use_decimal=True)
	# with open("./ctree_dblp/media/data/research_graph_" + user_ip + ".json", "wb") as json_file:
	# 	json_file.write(return_json)

	# matrix_mapping(career_period, matrix_data['pub'], matrix_data['coau'], ego, sy, ey, user_ip)


def matrix_mapping(career_period, publication, coauthors, ego, sy, ey, user_ip):
	matrix_egos = dict()
	matrix_egos["tree1"] = {'column': [], 'row': [], 'color': []}
	matrix_egos["tree2"] = {'column': [], 'row': [], 'color': []}
	matrix_egos["tree3"] = {'column': [], 'row': [], 'color': []}
	matrix_egos["tree4"] = {'column': [], 'row': [], 'color': []}
	period = ey - sy + 1

	color_gap = []
	start =  int(career_period[0])
	end = int(career_period[1])
	t_gap = int(career_period[2])
	
	for x in range(start+t_gap, end, t_gap):
		# print x
		color_gap.append(int(x))

	sort_publication = sorted(publication.items(), key=lambda p:getitem(p[1],'year'))
	sort_coauthor = sorted(coauthors.items(), key=lambda a:getitem(a[1],1))
	# sort_publication = {p:i for p,i in sort_publication}

	paper_data = 0
	for author, a_info in sort_coauthor:
		# print a_info[1]
		if author == ego[0]:
			print author
			author = 'self'

		matrix_egos["tree1"]["row"].append([author, a_info[0]])
		matrix_egos["tree2"]["row"].append([author, a_info[0]])
		for paper, p_info in sort_publication:
			# print p_info['year']
			if paper_data == 0:
				if p_info['author_order'] > 1:
					first_au = 0
				else:
					first_au = 1
				matrix_egos["tree1"]["column"].append([paper, p_info['pages'], first_au])
				matrix_egos["tree2"]["column"].append([paper, p_info['author_count']+1, first_au])

			cell_color = 0
			if paper in a_info[3]:
				if p_info['type'] == 'conf':
					cell_color = 1
				elif p_info['type'] == 'journals':
					cell_color = 3
				else:
					cell_color = 2
			matrix_egos["tree1"]["color"].append(cell_color)
			matrix_egos["tree2"]["color"].append(cell_color)
		paper_data += 1
		
	return_json = simplejson.dumps(matrix_egos, indent=4, use_decimal=True)
	with open("./ctree_dblp/media/data/research_matrix_" + user_ip + ".json", "wb") as json_file:
		json_file.write(return_json)
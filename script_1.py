from etherscan import Etherscan
import requests
import json
import time

etherscan_api = ""
os_api = ""


eth = Etherscan(etherscan_api)
rsb = 13449854
sb = 0000000000000
eb = 1000000000000

proof = "0x08D7C0242953446436F34b4C78Fe9da38c73668d"

class Nft:
	def __init__(self, address, tokenID, tokenName, tokenSymbol, tokenOwner="unknown"):
		self.address = address
		self.tokenID = tokenID
		self.tokenName = tokenName
		self.tokenSymbol = tokenSymbol
		self.tokenOwner = tokenOwner

		self.UID = address + "-" + str(tokenID)
		self.projectID = address + "-" + str()
		self.name = tokenName + " " + str(tokenID)
		self.transactions = []

	def __eq__(self, other):
		return self.UID == other.UID

class Wallet:
	def __init__(self, address):
		self.address = address

		self.nftsOwned = []
		self.nftsSold = []
		self.proofsOwned = 0

	def __eq__(self, other):
		return self.address == other.address


class Project:
	def __init__(self, name, wallet):
		self.name = name 
		self.proofOwners = [wallet]
		self.proofOwnedTokens = []

	def __eq__(self, other):
		return self.name == other.name


def get_owners(address):

	data = eth.get_erc721_token_transfer_events_by_contract_address_paginated(address, page=1, offset=10000, sort="asc")

	historic_owners = []
	owners = []
	sellers = []
	defecters = []

	test = []

	for d in data:
		w = Wallet(d['to'])
		if w not in historic_owners:
			historic_owners.append(w)


	for o in historic_owners:
		IN = 0
		OUT = 0
		for d in data:
			if o.address == d['to']:
				o.nftsOwned.append( Nft( d['contractAddress'], d['tokenID'], d['tokenName'], d['tokenSymbol']) )
			elif o.address == d['from']:
				o.nftsSold.append( Nft( d['contractAddress'], d['tokenID'], d['tokenName'], d['tokenSymbol']) )
		o.proofsOwned = len(o.nftsOwned) - len(o.nftsSold)

		if o.proofsOwned > 0:
			owners.append(o)

		elif o.proofsOwned == 0:
			defecters.append(o)

		else:
			sellers.append(o)

	return owners


def get_owners_bags(owners, project_retries = []):

	projects = project_retries
	retry = []

	sleep_count = 1

	count = 0

	for owner in owners:

		count += 1

		print("Starting " + str(count) + " of " + str(len(owners)))

		try:
		
			#print("")
			#print(owner.address)

			sleepTime = round(sleep_count/5, 2)

			if 2 <= sleep_count <= 50:
				print("Sleeping for " + str(sleepTime) + " seconds.")
				time.sleep(sleepTime)
			elif sleep_count >= 50:
				print("Sleeping for 5 seconds.")
				time.sleep(5)
			else:
				time.sleep(sleepTime)

				

			url = "https://api.opensea.io/api/v1/collections?asset_owner=" + owner.address + "&offset=0&limit=300"

			headers = {
		    	"Accept": "application/json",
		    	"X-API-KEY": os_api
			}

			response = requests.request("GET", url, headers=headers)


			#print(json.dumps(response.json(), indent=4, sort_keys=True))

			for p in response.json(): #list of projects the wallet owns at least one from

				project = Project(p['name'], owner)

				if project not in projects:
					projects.append(project)
				else:
					#print (next((x for x in projects if x.name == project.name), None))
					next((x for x in projects if x.name == project.name), None).proofOwners.append(owner)

			## remover after testing
			if count == 10000:
				break
			########################

			sleep_count = 0

		except:
			sleep_count += 1
			print ("Needs to be retried.\n")
			retry.append(owner)

		
	return [projects, retry]


holders = get_owners(proof)

results = get_owners_bags(holders)
projects = results[0]
retries = results[1]
retry_count =  len(results[1])

attempted_retries = 0
while retry_count > 0 and attempted_retries < 10:

	attempted_retries += 1

	print( "Starting retry number " + str(attempted_retries) + " in 10 seconds." )
	time.sleep(10)

	new_results = get_owners_bags(retries, projects)
	projects = new_results[0]
	retries = new_results[1]
	retry_count = len(new_results[1])


count = 0
projects.sort(key=lambda x: len(x.proofOwners), reverse=True)
for num, p in enumerate(projects, start=1):
	print (p.name + ", " +str(len(p.proofOwners)) + ", " + str(num))
	count += 1
	if count == 100:
		break

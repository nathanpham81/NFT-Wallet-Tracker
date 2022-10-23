# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 16:49:59 2022

@author: bpham
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 17:42:36 2022

@author: bpham
"""
import pickle
import random
import requests
import discord
from discord.ext import commands
import nest_asyncio
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import pytz
from datetime import datetime
from datetime import timedelta 
from discord.ext import tasks
from statistics import mean
from web3 import Web3






apikeys = ''
headers = {
    "Accept": "application/json",
    "X-API-KEY": ""
}

nest_asyncio.apply()

#Discord api key and declaring intent priveliges and creating the bot
TOKEN = ''
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='!', intents=intents)


               
#####################################################################################################################################
#Getting activity from the group 
#####################################################################################################################################               
@tasks.loop(seconds = 60)
async def routine():
    # group_buys ={}
    # group_listings = {}
    # group_unique_listers = {}
    # group_unique_buyers = {}
    
    
    notables ={}
    
    
    
    
    now = datetime.now(tz=pytz.UTC)
    future = now - timedelta(seconds = 60)
    future_str = future.strftime("%Y-%m-%dT%H:%M:%S")
    blocktime = future.timestamp()
    print(future_str)
    
    url = "https://api.opensea.io/api/v1/events"
    headers = {
        "Accept": "application/json",
        "X-API-KEY": ""
    }
    counter = 0
    for wallet in notables:
        
            
        headers['X-API-KEY'] = apikeys[random.randint(0,3)]
        querystring = { 'account_address': wallet, 'occurred_after': future_str, 'cursor': '' }
        print(counter)
        
        
        
        k = 1
        user_collection_list = {}
        user_collection_buy = {}
        user_collection_sold = {}
        user_collection_mint = {}
        
        ######################################################OpenSea###########################################################################
        while querystring['cursor'] != None and k >=1:
            
            headers['X-API-KEY'] = apikeys[random.randint(0,3)]
            response = requests.get(url, params = querystring,  headers=headers)
            h = response.json()
            # events = h['asset_events']
            
            try:
                events = h['asset_events']
            except:
                
                while True:
                    time.sleep(3.5)
                    headers['X-API-KEY'] = apikeys[random.randint(0,3)]
                    response = requests.get(url, params = querystring, headers=headers)
                    h = response.json()
                    
                    try:
                        events = h['asset_events']
                    except:
                        pass
                    else:
                        print('counter encountered an asset_event keyword error is fixed')
                        break
            else:
                pass
        

            
            for event in h['asset_events']:
                
                if event['event_type'] == 'created':
                    
                    #getting asset name
                    
                    asset_name = event['asset']['token_id']
                    if asset_name is None:
                        asset_name = event['collection_slug']
                        
                    #getting price   
                    price = int(event['ending_price'])/1000000000000000000
                    
                    #getting link to the asset
                    try:                            
                        link = event['asset']['permalink']
                    except:
                        link = 'https://opensea.io/' + wallet
                        
                    
                    # ###########print statements to see listing action##########################################################################
                
                    # print( notables[wallet] + ' has listed ' + asset_name + ' for ' + str(price) + ' ETH. Here is the link ' + link)
                    
                    
                    ################if listings then add to user specific activity dictionary##################################################
                    if user_collection_list.get(event['collection_slug']) == None:
                                               
                        user_collection_list[event['collection_slug']] = {'name': notables[wallet], 'prices': [price], 'id': [asset_name], 'link': [link]}
                    else:
                        
                        user_collection_list[event['collection_slug']]['prices'].append(price)
                        user_collection_list[event['collection_slug']]['id'].append(asset_name)
                        # user_collection_list[event['collection_slug']]['etherscan'].append(etherscan)
                        user_collection_list[event['collection_slug']]['link'].append(link)
                            

                #Notable wallet buys from OpenSea            
                elif event['event_type'] == 'successful' and event['winner_account']['address'] == wallet:
                
                    #getting asset name                    
                    asset_name = event['asset']['token_id']
                    if asset_name is None:
                        asset_name = event['collection_slug']
                        
                    #getting price    
                    price = int(event['total_price'])/1000000000000000000
                    
                    #getting link to asset
                    try:                           
                        link = event['asset']['permalink']                            
                    except:                             
                        link = 'https://opensea.io/' + wallet
                        
                    etherscan = 'https://etherscan.io/tx/' + event['transaction']['transaction_hash']
                    
                    ###########print statements to see listing action##########################################################################
                
                    # print( notables[wallet] + ' has bought ' + asset_name + ' for ' + str(price) + ' ETH. Here is the link ' + link)
                                                                
                    ################if buys then add to user specific activity dictionary##################################################

                    if user_collection_buy.get(event['collection_slug']) == None:
                                                
                        user_collection_buy[event['collection_slug']] = {'name': notables[wallet], 'prices': [price], 'id': [asset_name], 'link': [link], 'etherscan': [etherscan]}
                    else:
                         
                        user_collection_buy[event['collection_slug']]['prices'].append(price)
                        user_collection_buy[event['collection_slug']]['id'].append(asset_name)
                        user_collection_buy[event['collection_slug']]['etherscan'].append(etherscan)
                        user_collection_buy[event['collection_slug']]['link'].append(link)
                
                #Notable wallet sells on OpenSea        
                elif event['event_type'] == 'successful' and event['winner_account']['address'] != wallet:
                
                    #getting asset name                   
                    asset_name = event['asset']['token_id']
                    if asset_name is None:
                        asset_name = event['collection_slug']
                        
                    #getting price    
                    price = int(event['total_price'])/1000000000000000000
                    
                    #getting link to asset
                    try:                           
                        link = event['asset']['permalink']                            
                    except:                             
                        link = 'https://opensea.io/' + wallet
                        
                    etherscan = 'https://etherscan.io/tx/' + event['transaction']['transaction_hash']
                    
                    # print( notables[wallet] + ' has sold ' + asset_name + ' for ' + str(price) + ' ETH. Here is the link ' + link)

                    if user_collection_sold.get(event['collection_slug']) == None:                        
                        
                        user_collection_sold[event['collection_slug']] = {'name': notables[wallet], 'prices': [price], 'id': [asset_name], 'link': [link], 'etherscan': [etherscan]}
                    else:
                         
                        user_collection_sold[event['collection_slug']]['prices'].append(price)
                        user_collection_sold[event['collection_slug']]['id'].append(asset_name)
                        user_collection_sold[event['collection_slug']]['etherscan'].append(etherscan)
                        user_collection_sold[event['collection_slug']]['link'].append(link)
                            
                        
            querystring['cursor'] = h['next']
            k +=1
        #################################################Discord Message send after going through OS############################################
        if notables.get(wallet) != None and (len(user_collection_list) > 0 or len(user_collection_buy) > 0 or len(user_collection_sold) > 0):
            
            for guild in bot.guilds:
                
                if notables[wallet] in ['Zeneca_33', 'cirrrus', 'Nate_Rivers']:
                    channel = bot.get_channel()
                
                else:
                    channel = bot.get_channel()
                
                
                if len(user_collection_buy) > 0:
                    
                    embed = discord.Embed(title = notables[wallet] + ' has bought', url = 'https://opensea.io/' + notables[wallet] + '?tab=activity', color = discord.Color.green())
                    wallet_link = 'https://opensea.io/' + notables[wallet] + '?tab=activity'
                    for collection in user_collection_buy:
                        
                        if len(user_collection_buy[collection]['prices']) == 1:
                            item_link = user_collection_buy[collection]['link'][0]
                            etherscan_link = user_collection_buy[collection]['etherscan'][0]
                            embed.add_field(name = collection, value = 'Number bought: ' + str(len(user_collection_buy[collection]['prices'])) + ' | Avg Price: ' + str(round(mean(user_collection_buy[collection]['prices']),4)) + '\n IDs: ' + str(user_collection_buy[collection]['id']) + f"\n[item]({item_link}) | [etherscan]({etherscan_link}) | [os wallet]({wallet_link})", inline = False)
                        
                        else:
                            collection_link = 'https://opensea.io/collection/' + collection
                            embed.add_field(name = collection, value = 'Number bought: ' + str(len(user_collection_buy[collection]['prices'])) + ' | Avg Price: ' + str(round(mean(user_collection_buy[collection]['prices']),4)) + '\n IDs: ' + str(user_collection_buy[collection]['id']) +  f"\n[collection]({collection_link}) | [os wallet]({wallet_link})", inline = False)
            
            
                    # await channel.send(watcher_message)
                    await channel.send( embed = embed)
                    
                if len(user_collection_list) > 0:
                    
                    # watcher_message = f"{role.mention} a notable wallet has LISTED, see below."
                    embed = discord.Embed(title = notables[wallet] + ' has listed', url = 'https://opensea.io/' + notables[wallet] + '?tab=activity', color = discord.Color.red())
                    wallet_link = 'https://opensea.io/' + notables[wallet] + '?tab=activity'
                    
                    for collection in user_collection_list:
                        collection_link = 'https://opensea.io/collection/' + collection
                        embed.add_field(name = collection, value = 'Number listed: ' + str(len(user_collection_list[collection]['prices'])) + ' | Low Price: ' + str(round(min(user_collection_list[collection]['prices']),4)) + '\n IDs: ' + str(user_collection_list[collection]['id']) +  f"\n[collection]({collection_link}) | [os wallet]({wallet_link})", inline = False)
            
                    # await channel.send(watcher_message)
                    await channel.send( embed = embed)
                    
                if len(user_collection_sold) > 0:
                    
                    # watcher_message = f"{role.mention} a notable wallet has LISTED, see below."
                    embed = discord.Embed(title = notables[wallet] + ' has sold', url = 'https://opensea.io/' + notables[wallet] + '?tab=activity', color = discord.Color.blue())
                    wallet_link = 'https://opensea.io/' + notables[wallet] + '?tab=activity'
                    for collection in user_collection_sold:
                        
                        if len(user_collection_sold[collection]['prices']) == 1:
                            item_link = user_collection_sold[collection]['link'][0]
                            etherscan_link = user_collection_sold[collection]['etherscan'][0]
                            embed.add_field(name = collection, value = 'Number sold: ' + str(len(user_collection_sold[collection]['prices'])) + ' | Avg Price: ' + str(round(mean(user_collection_sold[collection]['prices']),2)) + '\n IDs: ' + str(user_collection_sold[collection]['id']) + f"\n[item]({item_link}) | [etherscan]({etherscan_link}) | [os wallet]({wallet_link})", inline = False)

                        else:
                            collection_link = 'https://opensea.io/collection/' + collection
                            embed.add_field(name = collection, value = 'Number sold: ' + str(len(user_collection_sold[collection]['prices'])) + ' | Avg Price: ' + str(round(mean(user_collection_sold[collection]['prices']),2)) + '\n IDs: ' + str(user_collection_sold[collection]['id']) + f"\n[collection]({collection_link}) | [os wallet]({wallet_link})", inline = False)
            
                    # await channel.send(watcher_message)
                    await channel.send( embed = embed)
                    
               

        #resetting variables after OpenSea run through
        user_collection_list = {}
        user_collection_buy = {}
        user_collection_sold = {}
        user_collection_mint = {}    
        #####################################################EtherScan##########################################################################
        url2 = "https://api.etherscan.io/api"
        #etherscan api key
        key = ''
        
        #initiating web3 object by connecting to Infura RPC on ethereum network
        w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/'))

        #txlist by address
        querystring2 = { "module": 'account', "action": 'tokennfttx',"address": wallet, 'startblock': 15741677, "endblock": 99999999, "page": 1, "offset": 30, "sort": 'desc', "apikey": key}
        response = requests.get(url2,params=querystring2)
        g = response.json()
        
        # try:
        #     events = h['asset_events']
        # except:
            
        #     while True:
        #         time.sleep(3.5)
        #         headers['X-API-KEY'] = apikeys[random.randint(0,1)]
        #         response = requests.get(url, params = querystring, headers=headers)
        #         h = response.json()
                
        #         try:
        #             events = h['asset_events']
        #         except:
        #             pass
        #         else:
        #             print('counter encountered an asset_event keyword error is fixed')
        #             break
        # else:
        #     pass
        try:
            
            for transaction in g['result']:
                if int(transaction['timeStamp']) < blocktime:
                    break
                else:
                    pass
                
                if transaction['from'] == '0x0000000000000000000000000000000000000000':
                    
                    asset_name = transaction['tokenName']
                    idnumber = transaction['tokenID']
                    
                    #getting link to asset
                    etherscan = 'https://etherscan.io/tx/' + transaction['hash']
                    contract = 'https://etherscan.io/address/' + transaction['contractAddress']
                    x2_link = 'https://x2y2.io/collection/'+ transaction['contractAddress'] + '/items'
                    
                    print( notables[wallet] + ' has minted ' + asset_name + '. Here is the link ' + etherscan)
    
                    if user_collection_mint.get(asset_name) == None:
                        
                        user_collection_mint[asset_name] = {'name': notables[wallet], 'id': [idnumber], 'etherscan': [etherscan], 'contract': contract, 'x2link': x2_link}
                    else:
                         
                        user_collection_mint[asset_name]['id'].append(idnumber)
                
                elif transaction['from'] == wallet:
                    
                    txs = w3.eth.get_transaction(transaction['hash'])
                    
                    if txs.to in ['0x74312363e45DCaBA76c59ec49a7Aa8A65a67EeD3', '0x83C8F28c26bF6aaca652Df1DbBE0e1b56F8baBa2', '0x39da41747a83aeE658334415666f3EF92DD0D541', '0x000000000000ad05ccc4f10045630fb830b95127']: #x2y2
                        
                        asset_name = transaction['tokenName']
                        idnumber = transaction['tokenID']
                            
                        #getting price    
                        #price = int(event['total_price'])/1000000000000000000
                        
                        #getting link to asset
                        etherscan = 'https://etherscan.io/tx/' + transaction['hash']
                        
                        print( notables[wallet] + ' has sold ' + asset_name + '. Here is the link ' + etherscan)
    
    
                        if user_collection_sold.get(asset_name) == None:                       
                            user_collection_sold[asset_name] = {'name': notables[wallet], 'id': [idnumber], 'etherscan': etherscan}
                        else:                         
                            # user_collection_sold[asset_name]['prices'].append(price)
                            user_collection_sold[asset_name]['id'].append(idnumber)
                
                elif transaction['to'] == wallet:
                    
                    txs = w3.eth.get_transaction(transaction['hash'])
                    
                    if txs.to in ['0x74312363e45DCaBA76c59ec49a7Aa8A65a67EeD3', '0x83C8F28c26bF6aaca652Df1DbBE0e1b56F8baBa2', '0x39da41747a83aeE658334415666f3EF92DD0D541']: #x2y2
                        
                        asset_name = transaction['tokenName']
                        idnumber = transaction['tokenID']
                            
                        #getting price    
                        # price = int(event['total_price'])/1000000000000000000
                        
                        #getting link to asset
                        etherscan = 'https://etherscan.io/tx/' + transaction['hash']
                        
                        print( notables[wallet] + ' has bought ' + asset_name + '. Here is the link ' + etherscan)
    
    
                        if user_collection_buy.get(asset_name) == None:                       
                            user_collection_buy[asset_name] = {'name': notables[wallet], 'id': [idnumber], 'etherscan': etherscan}
                        else:                         
                            # user_collection_buy[asset_name]['prices'].append(price)
                            user_collection_buy[asset_name]['id'].append(idnumber)
            
        except:
            pass
            
                                    
        
                                             
        ###################################################Sending Message in Discord before moving on to next wallet###########################
        if notables.get(wallet) != None and (len(user_collection_buy) > 0 or len(user_collection_sold) > 0 or len(user_collection_mint)) > 0:
            
            for guild in bot.guilds:
                
                if notables[wallet] in ['Zeneca_33', 'cirrrus', 'Nate_Rivers']   :
                    channel = bot.get_channel()
                
                else:
                    channel = bot.get_channel()
                
                # role = discord.utils.get(guild.roles, name='Underground Watchers')
                
                if len(user_collection_buy) > 0:
                    
                    # watcher_message = f"{role.mention} a notable wallet has BOUGHT, see below."
                    embed = discord.Embed(title = notables[wallet] + ' has bought', url = 'https://opensea.io/' + notables[wallet] + '?tab=activity', color = discord.Color.green())
                    wallet_link = 'https://opensea.io/' + notables[wallet] + '?tab=activity'
                    for collection in user_collection_buy:
                        #+ ' | Avg Price: ' + str(round(mean(user_collection_buy[collection]['prices']),2))
                        etherscan_link = user_collection_buy[collection]['etherscan']
                        embed.add_field(name = collection, value = 'Number bought: ' + str(len(user_collection_buy[collection]['id']))  + '\n IDs: ' + str(user_collection_buy[collection]['id']) + f"\n[etherscan]({etherscan_link}) | [os wallet]({wallet_link})", inline = False)
            
                    # await channel.send(watcher_message)
                    await channel.send( embed = embed)
                    
                if len(user_collection_mint) > 0:
                    
                    # watcher_message = f"{role.mention} a notable wallet has LISTED, see below."
                    embed = discord.Embed(title = notables[wallet] + ' has MINTED', url = 'https://opensea.io/' + notables[wallet] + '?tab=activity', color = discord.Color.yellow())
                    wallet_link = 'https://opensea.io/' + notables[wallet] + '?tab=activity'
                    for collection in user_collection_mint:
                        etherscan_link = user_collection_mint[collection]['etherscan'][0]
                        embed.add_field(name = collection, value = 'Number minted: ' + str(len(user_collection_mint[collection]['id']))  + '\n IDs: ' + str(user_collection_mint[collection]['id']) + f"\n[etherscan]({etherscan_link}) | [contract]({user_collection_mint[collection]['contract']}) | [x2y2 link]({user_collection_mint[collection]['x2link']}) | [os wallet]({wallet_link})", inline = False)
            
                    # await channel.send(watcher_message)
                    await channel.send( embed = embed)
                    
                if len(user_collection_sold) > 0:
                    
                    # watcher_message = f"{role.mention} a notable wallet has LISTED, see below."
                    embed = discord.Embed(title = notables[wallet] + ' has sold', url = 'https://opensea.io/' + notables[wallet] + '?tab=activity', color = discord.Color.blue())
                    wallet_link = 'https://opensea.io/' + notables[wallet] + '?tab=activity'
                    for collection in user_collection_sold:
                        #+ ' | Avg Price: ' + str(round(mean(user_collection_sold[collection]['prices']),2))
                        etherscan_link = user_collection_sold[collection]['etherscan']
                        embed.add_field(name = collection, value = 'Number sold: ' + str(len(user_collection_sold[collection]['id']))  + '\n IDs: ' + str(user_collection_sold[collection]['id']) + f"\n[etherscan]({etherscan_link}) | [os wallet]({wallet_link})", inline = False)
            
                    # await channel.send(watcher_message)
                    await channel.send( embed = embed)
                    

            
        counter +=1


        
@bot.event
async def on_ready():
    routine.start()

bot.run(TOKEN)        
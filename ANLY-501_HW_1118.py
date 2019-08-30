#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 17:46:07 2018

@author: yxy
"""

import matplotlib.pyplot as plt
from igraph import *
import igraph
import networkx as nx
import numpy as np
import pandas as pd

"""
May not all plots are going to be shown in the console but all will be saved as png files
"""

###############################################################################################################
    
def main():
    
    ## Small dataset with iGraph
    g=igraph.Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)])
    g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
    #g.vs.select(_degree = g.maxdegree())["name"]
    print(g)
    layout = g.layout("kk")
    igraph.plot(g, layout = layout,vertex_label=g.vs["name"]
        ,vertex_label_dist=2,vertex_label_angle=10,bbox=(300,300),margin=50)
    
    ###########################################################################
   
    ## Small dataset with networkx
    NetxG = nx.Graph()
    NetxG.add_nodes_from(["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"])
    #NetxG.add_edge(2, 3)
    NetxG.add_edges_from([("Alice","Bob"),("Alice","Claire"),("Claire","Dennis")
        ,("Dennis","Claire"),("Alice","Frank"),("George","Frank"),("Esther","Frank")])
    #print(list(NetxG.nodes))
    #print(list(NetxG.edges))
    plt.figure()
    plt.title('Small dataset with NetworkX',fontsize=20)
    nx.draw(NetxG,with_labels=True) 
    plt.show()
    
    ###########################################################################
    
    # Larger data preperation - SNA of Trump's Person-Person Edge List
    # Edgelist & Adjacency list is created by myself with the dataset above
    df1=pd.read_csv("Person_Person.csv",encoding = "ISO-8859-1")
    p_a=df1['Person A']
    p_b=df1['Person B']
    df2=pd.concat([p_a,p_b],axis=0)    
    df2_l=df2.values.tolist() # To count the frequency of names
    # Filter vertices - each one must know 2 or more people
    output = [] # Get unique values 
    for x in p_a:
        if x not in output:
            output.append(x)
    for x in p_b:
        if x not in output:
            output.append(x)
    #print (output)
    df3=pd.DataFrame(output)
    cnt=[]
    for x in output:
        cnt.append(df2_l.count(x))
    df3['cnt']=cnt # Add a new column of frequency of the names
    df4=df3
    df4=df4.drop(df3[df3.cnt>1].index) # Get the list the vertices with only 1 target
    df4_l=df4[0].values.tolist()# list the vertices with only 1 target
    # Drop the names who only know one person
    for x in df4_l:
        df1=df1[~df1['Person A'].str.contains(x)]
        df1=df1[~df1['Person B'].str.contains(x)]
        #df1=df1.reset_index(drop=True)
                # Since indices will be reset each time a row is dropped
                # If I set range(len(df1['Person A'])) it can be invalid after drops
                # because the number of indices is decreasing
                # So I set range(0,121) by running this loop over and over again to test out
                # And found that only 121 loops were necessary.
    p_a1=df1['Person A'].values.tolist()
    p_b1=df1['Person B'].values.tolist()
    output2 = [] # Get unique values again
    for x in p_a1:
        if x not in output2:
            output2.append(x)
    for x in p_b1:
        if x not in output2:
            output2.append(x)
    # Hence the number of viterces has been reduced from 232 to 89
    
    ###########################################################################
    
    ## igraph - edge list  
    l=list(zip(p_a1,p_b1)) # EDGELIST
    g1=igraph.Graph()
    g1.add_vertices(output2)
    g1.add_edges(l)
    #g1.vs.select(_degree_ge=2) 
    #g1.es.select(_source=2)
    #print(g1)
    layout = g1.layout("kk")
    igraph.plot(g1, layout = layout,vertex_label=output2
        ,vertex_label_dist=2,vertex_label_angle=10,bbox=(1500,1500),margin=100
        ,vertex_size=10,vertex_label_size=20).save('igraph - edge list.png')

    #g1.write_lgl('g1_lgl')# Create the adjacency list
    g1_lgl=df1.groupby('Person A')['Person B'].apply(','.join).reset_index()
    tfile = open('g1_lgl.txt', 'w')
    for i in range(len(g1_lgl['Person A'])):
        #tfile.write(g1_lgl['Person A'][i],g1_lgl['Person B'][i],'\n')
        tfile.write("%s,%s,%s" % (g1_lgl['Person A'][i],g1_lgl['Person B'][i],'\n'))
        #a=g1_lgl['Person A'][i]+' '+g1_lgl['Person B'][i]+'\n'
    tfile.close()
    g1.write_gml('g1_gml')# Create a gml file
    
    ## igraph - adjacency list (In fact adjacency matrix. Adjacency list is used in NetworkX down below.)
    adj_l = pd.crosstab(df1['Person A'],df1['Person B'])
    names=list(adj_l.columns.values)
    idx = adj_l.columns.union(adj_l.index) # Create the adjacency matrix
    adj_l = adj_l.reindex(index = idx, columns=idx, fill_value=0) # ADJACENCY LIST
    adj1=adj_l.as_matrix().tolist() # Convert the matrix into a list
    g2 = igraph.Graph.Adjacency(adj1)
    # plot the graph, just for fun
    igraph.plot(g2, layout = 'kk',vertex_label=names
        ,vertex_label_dist=2,vertex_label_angle=10,bbox=(1500,1500),margin=100
        ,vertex_size=10,vertex_label_size=20).save('igraph - adjacency list.png')
    
    ## igraph - weighted edges
    weights=[]
    for x in range(len(p_a1)):
        m=df3.loc[df3[0] == p_a1[x],'cnt'].iloc[0] # Add new features
        n=df3.loc[df3[0] == p_b1[x],'cnt'].iloc[0]
        mn=0.05*m/10*n
        weights.append(mn)
    g3=igraph.Graph()
    g3.add_vertices(output2)
    l=list(zip(p_a1,p_b1)) # EDGELIST
    for i in range(len(l)):
        g3.add_edge(l[i][0],l[i][1],weight=weights[i])
        #print(l[i][0],l[i][1],weights[i])
    #print(g3)
    layout = g3.layout("kk")
    igraph.plot(g3, layout = layout,vertex_label=output2
        ,vertex_label_dist=2,vertex_label_angle=10,bbox=(1500,1500),margin=100
        ,vertex_size=10,vertex_label_size=20,edge_width=weights).save('igraph - weighted edges.png')
    
    ## igraph - directed edges
    g4=igraph.Graph().as_directed() #use as.directed() to make it directed
    g4.add_vertices(output2)
    l=list(zip(p_a1,p_b1)) # EDGELIST
    for i in range(len(l)):
        g4.add_edge(l[i][0],l[i][1],weight=weights[i])
        #print(l[i][0],l[i][1],weights[i])
    #print(g4)
    layout = g4.layout("kk")
    #color_dict = {"1": "blue", "2": "pink", "3": "red", "4": "yellow", "57": "green", "5": "purple", "6": "black", "10": "orange"}
    #g4.vs["color"] = [color_dict[degree] for degree in g4.vs["degree"]]
    c_list=[]
    degree_list = g4.vs.degree()
    for x in degree_list:
        if x==1:
            c_list.append("blue")
        elif x==2:
            c_list.append("pink")
        elif x==3:
            c_list.append("red")
        elif x==4:
            c_list.append("yellow")
        elif x==57:
            c_list.append("green")
        elif x==5:
            c_list.append("purple")
        elif x==6:
            c_list.append("black")
        else:
            c_list.append("orange")     
    igraph.plot(g4, layout = layout,vertex_label=output2
        ,vertex_label_dist=2,vertex_label_angle=10,bbox=(2000,2000),margin=100
        ,vertex_size=10,vertex_label_size=20,edge_width=weights
        ,vertex_color=c_list).save('igraph - directed edges.png')
    
    ## igraph - gml
    g5=igraph.Graph.Read_GML('g1_gml')
    layout = g5.layout("kk")
    igraph.plot(g5, layout = layout,vertex_label=output2
        ,vertex_label_dist=2,vertex_label_angle=10,bbox=(1500,1500),margin=100
        ,vertex_size=10,vertex_label_size=20).save('igraph - gml.png')
    
    ###########################################################################
    
    ## networkx - edgelist
    NetxG1 = nx.Graph()
    NetxG1.add_nodes_from(output2)
    NetxG1.add_edges_from(l)
    #print(list(NetxG1.nodes))
    #print(list(NetxG1.edges))
    plt.figure(figsize=(25,25))
    plt.title('NetworkX - edgelist',fontsize=100)
    nx.draw(NetxG1,with_labels=True)
    plt.savefig('networkx - edgelist')
    
    ## networkx - adjacency list
    NetxG2 = nx.read_adjlist('g1_lgl.txt',delimiter=",", create_using = nx.DiGraph(), nodetype = str)
    #NetxG2 = nx.from_pandas_dataframe(g1_lgl,'Person A','Person B')
    plt.figure(figsize=(25,25))
    plt.title('NetworkX - adjacency list',fontsize=100)
    nx.draw(NetxG2,with_labels=True)
    #plt.show()
    plt.savefig('networkx - adjacency list')
    
    ## networkx - weighted edges
    weighted_eg=[]
    for i in range(len(l)): # Create a weighted edge list
        weighted_eg.append([l[i][0],l[i][1],weights[i]])
    NetxG3=nx.Graph()
    NetxG3.add_weighted_edges_from(weighted_eg)
    plt.figure(figsize=(25,25))
    plt.title('NetworkX - weighted edgelist',fontsize=100)
    nx.draw(NetxG3,with_labels=True,width=weights)
    plt.savefig('networkx - weighted edge list') 
    
    ## networkx - directed edges
    NetxG4=nx.DiGraph()
    NetxG4.add_weighted_edges_from(weighted_eg)
    plt.figure(figsize=(25,25)) 
    plt.title('NetworkX - weighted & directed edges with colored nodes',fontsize=50)
    nx.draw(NetxG4,with_labels=True,arrowsize=30,node_color = c_list,node_size=200,width=weights)
    plt.savefig('networkx - directed edges')
    
    ## networkx - gml
    NetxG5 = nx.read_gml('karate.gml',label='id') 
         # This version of networkx has some problem with reading gml files
         # If I wanna use the gml I created with igraph, I'd have to downgrade networkx
         # Therefore I used another dataset downloaded from internet
    plt.figure(5,figsize=(25,25)) 
    plt.title('NetworkX - gml',fontsize=100)
    nx.draw(NetxG5,with_labels=True)
    plt.savefig('networkx - gml')
    
###############################################################################################################

if __name__ == "__main__":
    main()    

    
    
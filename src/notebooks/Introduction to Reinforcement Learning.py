#!/usr/bin/env python
# coding: utf-8

# # Introduction to Reinforcement Learning
# 
# This notebook is a walkthrough of applying reinforcement learning on different problems using the keras and tensorflow backend neural network over Q-Learning algorithm

# ### Section 1: Libraries and Modules

# In[2]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
sns.set()

import tensorflow as tf
import keras.backend as K

import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory


# In[3]:


import warnings
warnings.filterwarnings('ignore')


# ## Cartpole Problem

# ### Section 2: Defining the Environment

# In[2]:


ENV_NAME = 'CartPole-v0'

# Get the environment and extract the number of actions available in the Cartpole problem
env = gym.make(ENV_NAME)
np.random.seed(123)
env.seed(123)
nb_actions = env.action_space.n


# ### Section 3: Defining the ANN Architecture

# In[13]:


model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(8))
model.add(Activation('relu'))
model.add(Dense(8))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
model.summary()


# ### Section 4: Training the Model using the Q-Learning Algorithm

# In[14]:


policy = EpsGreedyQPolicy()
memory = SequentialMemory(limit=50000, window_length=1)
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this slows down training quite a lot. 
dqn.fit(env, nb_steps=5000, visualize=False, verbose=2)


# In[16]:


dqn.test(env, nb_episodes=10, visualize=True)


# ## Ant Problem

# ### Section 2: Defining the Environment

# In[12]:


ENV_NAME = 'MountainCar-v0'

# Get the environment and extract the number of actions available in the Cartpole problem
env = gym.make(ENV_NAME)
np.random.seed(123)
env.seed(123)
nb_actions = env.action_space.n


# ### Section 3: Defining the ANN Architecture

# In[76]:


model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
model.summary()


# ### Section 4: Training the Model using the Q-Learning Algorithm

# In[84]:


policy = EpsGreedyQPolicy()
memory = SequentialMemory(limit=50000, window_length=1)
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=400,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this slows down training quite a lot. 
dqn.fit(env, nb_steps=10000, visualize=False, verbose=1)


# In[85]:


dqn.test(env, nb_episodes=5, visualize=True)
env.close()


# ### Section 5: Random Action

# In[68]:


env.reset()
action = 0
for i in range(1000):
    env.render()
    if i < 400:
        env.step(0) # take a random action
    else:
        env.step(2) # take a random action
        # env.step(env.action_space.sample()) # take a random action
env.close()


import math
import numpy as np
from get_data import GetData



class Environment:

    def __init__(self, WINDOW_LENGTH, EPOCHS, BATCH_SIZE, symbol):
        self.WINDOW_LENGTH = WINDOW_LENGTH
        self.EPOCHS = EPOCHS
        self.BATCH_SIZE = BATCH_SIZE

        self.data = GetData(symbol).format_data()
        self.data_len = len(self.data)

        self.total_profit = 0
        self.max__profit = 0
        self.already_bought = False
        self.buy_count = 0
        self.sell_count = 0
        self.history = []



    def get_state(self, t, n):
        """
            Function to break the data up into window sized chunks
            :return:
        """

        def sigmoid(x):
            return 1 / (1 + math.exp(-x))

        d = t - n + 1
        block = self.data[d:t + 1] if d >= 0 else np.append(-d * [self.data[0]], self.data[0:t + 1])  # pad with t0
        res = []
        for i in range(n - 1):
            res.append(sigmoid(block[i + 1] - block[i]))

        return np.array([res])

    def determine_reward(self, agent, action, t):
        """
        Function that will determine the reward for the agent depending on the action
        For a buy, we check how many better options there were (where the price was cheaper)
        For a sell, we check if there was a better time to sell (where the price was more expensive

        :param agent:
        :param action:
        :param t:
        :return:
        """

        reward = 0
        profit = 0

        if action == 1 :  # Buy only if we already have less than 6 active buy orders
        # Having a limit on the number of buys is a more realistic way of trading

            self.buy_count += 1
            self.history.append('B')
            agent.inventory.append(self.data[t])

            # Check to see if we could have bought at a better time
            min_count = 0
            for i in range(1, self.WINDOW_LENGTH - 1):
                try:
                    if self.data[t-i:t] < self.data[t]:
                        min_count += 1
                except:
                    break

            # For every better option, subtract 0.1 from a total of 1 possible point
            reward = 0.5 - (0.1 * min_count)

            #print('Buy at ' + str(self.data[t]))
            # print(str(min_count) + ' possible buys that were better, got a reward of ' + str(reward) + ' out of 1 \n')

        elif action == 2 and len(agent.inventory) > 0:  # sell
            self.history.append('S')
            self.sell_count += 1
            bought_price = min(agent.inventory)
            agent.inventory.remove(bought_price)
            reward = max(self.data[t] - bought_price, 0)
            profit = self.data[t] - bought_price

            self.total_profit += profit

            self.already_bought = False

            if profit > 0: # We made profit, it's at least a decent trade
                # If we were profitable, we add an immediate 0.7 / 1.0
                reward = 0.8 * profit

            # Check if we could have bought at a higher price
            max_count = 0
            for i in range(1, self.WINDOW_LENGTH - 1):
                try:
                    if self.data[t-i:t] < self.data[t]:
                        max_count += 1
                except:
                    break

            # For every price that was potentially higher, we subtract 0.03 from a possible 0.3 for this component
            reward += 0.2 - (0.02 * max_count)


            #print('Sold at ' + str(self.data[t]))
            # print(str(max_count) + ' possible buys that were better, got a reward of ' + str(reward) + ' out of 1 \n')
            #print('Profit of : ' + str(profit))
        return reward, profit



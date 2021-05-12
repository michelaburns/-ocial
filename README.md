# $ocial

## Introduction
* Thanks to the recent unprecedented success of Bitcoin (BTC) and Ethereum (ETC), the alternative cryptocurrency market is seeing a rapid free-for-all.
Both old and new altcoins (cryptocurrencies other than BTC) are garnering more and more support as individuals catch the cryptocurrency craze. 
Social media platforms are ablaze with posts speculating what the next best coin is and how you need to invest now to make it big!
But how much of this is talk is just hype?
Within my project, I analyzed 21 cryptocurrencies' Twitter activity and market performance from the start of 2021 to the end of April 2021 to 
determine whether or not the cryptocurrencies’ daily price momentum can be predicted via Twitter activity.
* Cryptocurrencies
  * Aave ($AAVE)
  * Avalanche ($AVAX)
  * Cardano ($ADA)
  * Chainlink ($LINK)
  * Dash ($DASH)
  * Dogecoin ($DOGE)
  * EOS ($EOS)
  * Hedera Hashgraph ($HBAR)
  * IOTA ($MIOTA)
  * Litecoin ($LTC)
  * Maker ($MKR)
  * Monero ($XMR)
  * Polkadot ($DOT)
  * Solana ($SOL)
  * Stellar ($XLM)
  * Tether ($USDT)
  * Theta ($THETA)
  * Tron ($TRX)
  * Uniswap ($UNI)
  * VeChain ($VET)
  * XRP ($XRP)

## Files
* **cryptocurrency_data**: Folder containing CSV files for the daily market data from 01-01-2021 to 04-30-2021 (inclusive) from Investing.com for all of the 21 cryptocurrencies
* **twitter_clean**: Folder containing CSV files for the cleaned daily Twitter activity from 01-01-2021 to 04-30-2021 (inclusive) for all of the 21 cryptocurrencies
* **twitter_unclean**: Folder containing uncleaned Twitter data. twitter_unclean has folders for each of the 21 cryptocurrencies. Each cryptocurrency folder contains a "tweets_2021" folder, which contains 4 folders (01, 02, 03, 04) for January 2021, February 2021, March 2021, and April 2021. Each of the month folders contains compressed csv files that have uncleaned Twitter data for each day of the month
* **combined_final.csv**: CSV file with the cryptocurrency and clean Twitter data combined
* **final_code.ipynb**: Ipython notebook that includes...
   * Cleaning and combining the Investing.com cryptocurrency market data (cryptocurrency_data) and clean Twitter data (twitter_clean) into a single Pandas DataFrame
   * Running various machine learning models on the final dataset to predict the cryptocurrencies’ daily price momentum
     * Linear Trend Model
     * Random Walk Model
     * Simple Auto-Regressive Model
     * Higher-Order Auto-Regressive Model
* **twitter.py**: Python script that utilizes multiprocessing and threading to efficiently web scrape tweets containing a cryptocurrency’s cashtag
* **twitter_cleaning.ipynb**: Ipython notebook that cleans, analyzes, and aggregates the Twitter data for each cryptocurrency


## Data
* **combined_final**
  * date
  * symbol
  * momentum
  * num_tweets
  * replies_sum
  * retweets_sum
  * likes_sum 
  * subjectivity_sum
  * polarity_sum
  * replies_avg
  * retweets_avg
  * likes_avg
  * subjectivity_avg
  * polarity_avg
  * tone_most_common

# AUCTION WEBSITE
#### Video Demo:  <https://www.youtube.com/watch?v=fKgkqorce9g>
#### Description:
**AUCTION WEBSITE** in its most basic form is a website designed to allow users to add items for auction and bid on auctioned items in real time. It is designed as a user friendly website with basic security protection. This website could be used for a live auction, to sell tickets for a concert beginning in a few hours, a garage sale, inventory clearance, items stored in a warehouse, even cryotocurrency exchange.
The website accepts items for auction, allows multiple bids, specifies an end time for each auction item, awards successful bids with automatic messaging, identifies items which did not receive a bid for archival and transfers cash between the successful bidder and the seller. There are some checks and balances to ensure that the certain fields only accept certain formats such as positive numbers for prices or duration.
I have tried to build certain features of CraigsList such as allowing a seller to put up items for sale and suggest a price, and certain features of a site such as Priceline which had a feature to allow users to set their own price for a ticket.

**Design Basis**. This website has been designed using Python, Flask, sqlite3, html, css, bootstrap and jinja. Features built into this program include time calculation, key sharing between database tables, dynamic update of tables, row indexing, try/except coding, flash messaging, etc. The base command to start the website is flask run.

In future, the code can be modified in various ways to have a user add cash to their balance, have a feature to hold the withdrawal until the buyer verifies goods received, or to have the seller deposit the goods with a thrid party for verification of the goods. Credit card transactions is another feature which could be added.

**Logic**. The logic applied in the app.py file is briefly as follows. The user can be a bidder or seller. Each user has placed some cash to make bids. When making a bid, the available cash for the user is verified to be greater than the bid amount and the position then adjusted where the bid amount is removed from this field and placed in hold until the final award for this auction item is made. The user can only place bids on items they themselves have not put up for bid, so that the user cannot manipulate the bid price once it is placed. This is done by having the Submit button grayed out for the bids created by the user themselves. Once the endtime is reached, the website removes the bid from the display and places it in the Sold Items list. It does so by logic in the app.py file, which searches for the last bid at the time of bid expiry, converting this into the bought and sold price, and identifying the last bidder as the buyer. The buyer and seller are messaged about this transaction. The cash for the bid is transferred from the buyer to the seller and their cash positions are updated. If no bid has been placed on the item, it is archived without an award and the seller is notified. The program ensures that each bid is higher than the previous bid.

The auction database contains three tables, viz. **users**, **items** and **history**. These tables are cross-linked through use of the users (id) key and the items (item_id) key. The users table has the user information and cash position, while the items table has the more permanent type of information about the auction items. THe history key updates every time a bid is placed, awarded or archived.

The initial screen enables the user to register or log in through the **Register** and **Log In** links.. Tirst step is for a user to register with a username and password, which is hashed for security. The user can subsequently log in using this username and password.

Once the user logs in the screen changes to an index page which displaya a menu bar at the top allowing the user to click on various actionable and informational features of the website. At the top right, the user is able to change their password or log out of the session through the **Change Password** and **Log Out** links. The index page also displays all auction items available at that time.

At the top left are several webpage links which allow user queries and actions, which are described below.

**Make a Bid**. The bids that are displayed on the index page are also accessed from any other screen by clicking on this link at the top. This feature allows users to look at the items available for bid, describing the item, showing the latest bid price, showing the end time allowable for the last bid, and a final column which allows the user to place a bid via a Submit button.

**My Bid History**. This link has details of the bids placed by the logged in user for each item and is grouped by item.

**Sell New Item**. this link allows the user to create a new auction item inputting details of the item such as name, class and description, setting a starting price and an end time when the bid will be removed from the active bidding list.

**My Items on Auction**. This link contains a history of all items added by the user that are presently being auctioned.

**Items I Bought**. This links to a list of all items which have been purchased by the user to date.

**Items I Sold**. This links to the list of all items successfully sold by the logged in user. Items which did not receive a bid are excluded from this list.

**All Items Sold**. This links to a list of all items sold on this website with their final purchase price.

**My Cash**. This provides the user with a snapshot of their cash position, separating it into cash available for bidding and cash held in escrow for bids currently placed on auctioned items.

**Challenges** Challenges in developing the program were, among others, in tying databases together, in preparing the logic for the completion of the bid process, calculating cash positions, preparing the request forms, and making the site user friendly. Extracting the values out of the rows also required some leg work, as the format of the rows such as a dicitonary within a list, needed proper indexing to reach the core value. This program was developed without collaboration with others, thus it invovled developing all parts of the code, with a couple of false starts. The Internet was extensively used to  get access to syntax and features of various programs. The exercise for the Finance database developed during the CS50 course was very useful to understand the interrelationships between the various languages and to use as a starting point for this website. The cat from the apology file stays.

**Other realizations** it appears that several websites such as CraigsList, PRiceline, eBay, Amazon, all seem to share a basic structure for their exhibition and sale of goods. It felt during program development that basic websites with these same functions are not far out of reach of the tools which were presented in the CS50 course. Python is very powerful for simply the ease of writing code and its libraries. I found certain features of flask and jinja to be a little challenging, especially pulling out individual row data from multiple rows.

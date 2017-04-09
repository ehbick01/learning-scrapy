Understanding the Infrastructure
===

## AWS DynamoDB
DynamoDB is a hosted database service that is part of the Amazon Web Services (AWS) suite. You can read/write from/to it from Python - and if you are running Python scripts remotely in AWS then it makes sense to keep the database in the same place.

## Getting Started

** Step 1: Create a table**

After signing into the AWS Console, navigate to DynamoDB and click "Create a Table."  Once you set the table name, define what variable you want to partition your data against. This partition will apply across all of your data, so you want to be the most uniquely identifiable element across as many variables as possible (such as a name, or an account number).

After you do that, you want to create a sort key against variables of interest. This could be a list of reviews attributed to the name/account, or anything that could duplicate your partition variable.

**Step 2: Throw some data at it**

The first step here is to create an IAM user with dynamoDB access in the IAM console. For the sake of learning, I created one and generated my access keys to feed into my resource call.

Once the user is created, build the table using [create_table.py](create_table.py) - which will build a table and define the schema.

Once the table is built, running [load_data.py](load_data.py) will populate the table with the data stored in JSON format. The `put_item` function will assign each variable to its appropriate classification 

When you look at the AWS dynamoDB console - the new table with data will be there!
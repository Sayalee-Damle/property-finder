system_message = "You are an expert in extracting informtaion"

human_message = """
You will be given a message: {user_input}, please extract the following attributes
1. property type
2. minimum number of bedrooms
return result in a JSON format, with key value pairs.
Please give the result only after this sentence 'the result in JSON format would be:'
"""
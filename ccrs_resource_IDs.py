# Type, Year:Resource_ID from https://lab.data.ca.gov/dataset/ccrs
crashes = {}
parties = {}
injuries = {}
crashes['2025'] = '9f4fc839-122d-4595-a146-43bc4ed16f46'
parties['2025'] = 'a2676918-a825-4b77-8e5c-6eadb38d6b1a'
injuries['2025'] = '10184ea3-7411-42d8-87a6-17039b58f04b'
crashes['2024'] = 'f775df59-b89b-4f82-bd3d-8807fa3a22a0'
parties['2024'] = '93892d36-017b-4a2a-bc0b-f1f385060b96'
injuries['2024'] = 'a36a0078-d7e1-4244-8337-0a59433c9b84'
crashes['2023'] = '436642c0-cd04-4a4c-b45e-564b66437476'
parties['2023'] = '84376be5-548b-44e3-8ebc-73e8a2ca9945'
injuries['2023'] = '1dfc36fa-a5dd-4616-b9b0-ff55699e299a'
crashes['2022'] = '7828780b-117b-455e-9275-986ad3ffde50'
parties['2022'] = '9ef51178-51cb-4939-9344-2d0907740580'
injuries['2022'] = '2d9e8bef-d5a2-402e-82eb-6386ad4d09f7'
crashes['2021'] = 'd08692e2-6d36-487e-bca0-28cd127a626f'
parties['2021'] = '754fe00c-f3bf-4f2f-80d0-ed4aa7b89b77'
injuries['2021'] = '616a9850-27cb-4012-b6e7-90a2e495900a'
crashes['2020'] = 'a2e0605d-0695-4bce-806d-4d0dda7ace68'
parties['2020'] = 'ebfed5da-82d6-4af2-bf40-b9516d7935a9'
injuries['2020'] = '459a4ce9-2a2a-4c50-a3fc-cfd6d4cbfa6e'
crashes['2019'] = '2b4c7d03-e684-435e-80da-17935de9499f'
parties['2019'] = '1a06775e-7d4a-4574-b3d4-f815d02d236a'
injuries['2019'] = '8ad780b4-0a05-4258-a461-57254888eb1a'
crashes['2018'] = 'a4b57216-5110-43d3-884c-d95366b19158'
parties['2018'] = '42f3f3d1-c130-4ebc-9536-98bf7880b0b9'
injuries['2018'] = 'ca547c12-f64d-4b6a-8f25-7075f6d6ec0b'
crashes['2017'] = '4784664d-b7cf-4427-af25-7c7307bad56c'
parties['2017'] = 'e8c625e8-674a-49f2-abe9-405267613045'
injuries['2017'] = 'fcb4f72e-db37-4379-8b78-25aad557d6cb'
crashes['2016'] = '3d5f2586-cf68-4213-aa1c-60df37399d10'
parties['2016'] = '2e8e3d81-4615-4b8e-ab7f-408f10f64bba'
injuries['2016'] = 'ea0bb73d-c41c-4d15-8a88-0c2a51fcd33a'


def CCRS_resource_IDs(year):
    year = str(year)
    return crashes[year], parties[year], injuries[year]

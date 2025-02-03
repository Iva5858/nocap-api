#!/usr/bin/env python
import warnings
import os
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from veritas_fact_check_api.crew import InstagramFactCheckCrew

def run():
    """
    Run the Instagram fact-checking crew.
    """
    # Example input dictionary
    post_data =  {"username" : "nytimes", "description" : "There is no shortage of unpleasant odors in New York City, but this week New Yorkers flocked to one foul scent: the blooming of an Amorphophallus gigas, a.k.a. a corpse flower, at the Brooklyn Botanic Garden. The plant's smell, resembling that of rotten flesh, is meant to attract pollinators like beetles and flies that are typically drawn to dead animals. When the garden announced the bloom's arrival on social media on Friday morning, New Yorkers skipped work and canceled plans, rushing to bear witness to the natural wonder. It flowers only every three to five years after its first time, which can take nearly a decade. One visitor described the odor as similar to that of 'briny, dead fish.' Another compared it to that of a dead rat. 'I was familiar with this plant but only in a textbook way, so this is special,' said Aprajita Singh, who was among the first to experience the gigas in full bloom. Read more about the rare plant at the link in our bio. Photos by @adriennegrunwald", "post_url" : "https://scontent-cdg4-3.cdninstagram.com/v/t51.2885-15/475112038_517521467447458_4047670216010397902_n.jpg?stp=dst-jpg_e35_p720x720_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xMDgweDEzNTAuc2RyLmYyODg1LmRlZmF1bHRfaW1hZ2UifQ&_nc_ht=scontent-cdg4-3.cdninstagram.com&_nc_cat=1&_nc_ohc=D3S2soTLUekQ7kNvgFU68u6&_nc_gid=4fe05bab400745719fea340c73f05ac8&edm=AP4sbd4BAAAA&ccb=7-5&ig_cache_key=MzU1MzYzMjcxNjM1NDYyMjIxMQ%3D%3D.3-ccb7-5&oh=00_AYBrTgQjM1OsZvqGA4NOUC5l34qZ3ftfioDi3jfJrgck0w&oe=679D33CC&_nc_sid=7a9f4b", "time_test" : 1234567890}
    
    
    crew = InstagramFactCheckCrew()
    result = crew.run(post_data)
    
    if result['message'][0].get('content'):
        content = result['message'][0]['content']
        if len(content) <= 850:
            print(content)  # Print only the content
        else:
            print("Error: Content exceeds 850 character limit")
    else:
        print("Error:", result['message'][0].get('error', 'Unknown error'))

if __name__ == "__main__":
    run()

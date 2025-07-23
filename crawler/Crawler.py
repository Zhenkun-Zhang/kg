import TransformersCrawler, PaddleNLPCrawler
def main():
    # 爬取 Transformers 算子信息
    version = 'main'
    root = "https://huggingface.co/docs/transformers/" + version + "/en/"
    save_path = "dao/node/Transformers/"+ version + "/"
    TransformersCrawler.solve(root, save_path, version)
    
    
if __name__ == '__main__':
    main()

# python src/crawler/Crawler.py

# Kelimeler.net Crawler

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
scrapy crawl kelimeler -O questions.json
```
```bash
scrapy crawl bulurum -a what=eczane -a where=izmir -o bulurum.csv
```
```bash
scrapy crawl bulurum -a what=eczane -a where=izmir -o bulurum.xlsx
```

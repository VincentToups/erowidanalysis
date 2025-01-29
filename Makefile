.PHONY: clean

clean:
	rm -rf derived_data

derived_data/experience_urls.csv: get_urls.py
	python3 get_urls.py

derived_data/experience_data.csv derived_data/doses_data.csv: get_page_data.py derived_data/experience_urls.csv
	python3 get_page_data.py

derived_data/archetypes.csv: derived_data/summaries.csv archetypes.py
	python3 archetypes.py

derived_data/summaries.csv: derived_data/experience_data.csv summarize.py
	derived_data/summaries.csv

figures/archetype_histogram.png: derived_data/archetypes.csv derived_data/experience_data.csv derived_data/doses_data.csv arch_histo.R
	Rscript arch_histo.R

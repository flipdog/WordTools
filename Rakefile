require 'rake/clean'
CLEAN.include("data/*.pck")

file "data/raw_onegrams.pck" => ["gen_ngrams.py"] do
	sh "mkdir -p data"
	sh "python gen_ngrams.py"
end

task :data => ["data/raw_onegrams.pck"]
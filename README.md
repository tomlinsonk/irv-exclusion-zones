This repository accompanies the paper:
> Kiran Tomlinson, Johan Ugander, and Jon Kleinberg. (2025) Exclusion Zones of Instant Runoff Voting. https://arxiv.org/abs/2502.16719


## Files
- `graph_exclusion.py`: Code implementing IRV on graphs, our optimized FPT algorithm, and our approximation algorithm.
- `plot.py`: For displaying results of experiments.
- `preprocess_schools.py`: For processing the New Jersey schools data.
- `graph-voting-c/`: A C implementation of IRV on graphs and of our approximation algorithm (considerably faster than the Python implementation)
- `results/`: the results of our experiment runs

## Requirements
We used (although newer versions will likely work fine):
- python 3.11.7
	- tqdm 4.66.2
	- matplotlib 3.8.2
	- numpy 1.26.4
	- networkx 3.2.1
- for graph-voting-c:
	- clang 15.0.0
	- GNU make 3.81

## Data
The New Jersey schools data is available for download at: https://doi.org/10.3886/ICPSR37070.v2. Place the `ICPSR_37070/` folder inside a directory called `data/` in the repository. After doing this, run `python3 preprocess_schools.py` to generate `data/schools/*.txt`.


# Running the experiments
First, download and preprocess the schools data as described above.

Run `python3 plot.py` to use our existing results files and display all results used in the paper, including the tables and plots (placed in `plots/`).

Run `python3 graph_exlcusion.py` to rerun the exhaustive search of small graphs and trees.

To run the approximation algorithm on the 56 school networks, we used 30 cores on a server so that we could run on schools in parallel. First, run `make clean` and `make` in `graph-voting-c`. (If you have a C compiler other than clang, you will need to change the compiler in `graph-voting-c/Makefile`.) Then, to run the `graph_voting` executable on schools in 30 parallel processes, we used:
 `find ../data/schools/*.txt -print0 | xargs -0 -t -I % -P 30 ./graph_voting %`. 



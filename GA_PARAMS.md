### GA params 

The GA parameters for the NSGA-II implementation were selected based on the parameters for solving Min-Ex problem with 
the same algorithm in Multi-Objective Optimization Using Evolutionary Algorithms by Kalyanmoy Deb.

| Parameter      | Value     | 
|----------------|-----------|
| Crossover rate | 0.9       | 
| Mut. rate      | 0 or 0.02 |
| Pop. size      | 40        | 
| Generations    | 50        | 


in python command: 

```bash
python3 -m python.main_optimizer \
--crossover-rate 0.9 \
--mutation-rate 0.02 \
--population-size 40 \
--generations 50
```

# Solution caching 

For optimization with a population of 40 solutions over 50 generations, the total number of evaluations should be 40 × 50 = 2,000 solutions.

In the first test run, only 753 solutions were unique. The evaluation time was 1,038 minutes for all 2,000 solutions. 

After applying solution caching, the expected performance boost can be calculated as follows:

2,000 solutions → 1,038 minutes
753 solutions → x minutes

Setting up the proportion:
2,000 / 1,038 = 753 / x

Cross-multiplying:
2,000x = 1,038 × 753
2,000x = 781,614

Solving for x:
x = 781,614 / 2,000
x ≈ 391 minutes

This results in a speedup of:
1,038 / 391 ≈ 2.66×

Therefore, solution caching provides approximately a 2.66× performance improvement.

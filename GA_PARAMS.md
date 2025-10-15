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
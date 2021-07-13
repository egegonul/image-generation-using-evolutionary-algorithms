# image-generation-using-evolutionary-algorithms

The pseudocode for the algorithm is as follows:,

Initialize population with <num_inds> individuals each having <num_genes> genes
While not all generations (<num_generations>) are computed:
Evaluate all the individuals
Select individuals
Do crossover on some individuals
Mutate some individuals

*Individuals*

Each individual has one chromosome. Each gene in a chromosome represents one circle to be drawn.
Each gene has at least 7 values:
* The center coordinates, (x, y)
* The radius, radius ∈ Z+
* The color (red, R ∈ Z, green, G ∈ Z, blue, B ∈ Z, alpha, A ∈ R) where (R, G, B) ∈ [0, 255] and
A ∈ [0, 1]

*Evaluation*

In order to evaluate an individual, its corresponding image should be drawn first. Note that the chromosome order is important. The pseudocode is as follows:
Initialize <image> completely white with the same shape as the <source_image>.
For each gene in the chromosome:
overlay <- image
Draw the circle on overlay.
image <- overlay x alpha + image x (1-alpha)
  



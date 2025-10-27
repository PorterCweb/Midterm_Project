A <- matrix(c(1, 2, 3, 
              2, 4, 2, 
              0, 0, 1), nrow = 3, byrow = TRUE);
B = A
for (i in 1:9) 
{
  B <- B %*% A
}
B <- t(B)
print(B)




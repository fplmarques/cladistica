#!/usr/bin/R
v <- seq(0,1,by=0.001)
n_sub <- 3
n_nosub <- 9
e <- sum(1/factorial(0:100))
for (i in v){
sub <- 1/4-(1/4*(e^(-4*(v/3))))
nosub <- 1/4+(3/4*(e^(-4*(v/3))))
L <- c((sub^n_sub)*(nosub^n_nosub))
}
maxL <- max(L)
indexL <- match(maxL,L)
best_v <- v[indexL]
pdf("plot_3.pdf")
plot(v, L, xlab="v", ylab="L", col="blue", frame=F, pch=16,cex=0.5)
#text(0.8, maxL, paste("L =", maxL, "\n v =", best_v))
dev.off()


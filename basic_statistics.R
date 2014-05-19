is.normal <- function(data) {
  if (length(data)<3) { return(F) }
  if (all(data==data[1])) { return(F) }
  return(shapiro.test(data)[2]>0.05)
}

PID = 'display_name'
TID = 'team_abbreviation'
bs = fread("boxscores.csv")
teams = fread("teams.csv")

bs[,N:=.N,by=PID]
bss = bs[N>30, list(
  avg.pts=mean(points), 
  sd.pts=sd(points), 
  var.pts=var(points), 
  position=unique(position)[1],
  last_name=unique(last_name)[1],
  team=unique(team_abbreviation)[1]), 
       by=PID]
bss[, position:=factor(position,levels=c("C","PF","SF","SG","PG"))]
names(bss)
dim(bss)


lm_fit  = lm(var.pts ~ avg.pts + 0, data = bss)
bss.pred = data.table(bss, predict(lm_fit, interval = 'prediction'))
names(bss.pred)

q = qplot(x=avg.pts, y=var.pts/avg.pts, data=bss.pred) +
  scale_color_brewer(palette="Set1") + 
  labs(x="point average", y="ajdusted point variance")
q1 = q #+ geom_ribbon(aes(y = sqrt(fit), ymin = sqrt(lwr), ymax = sqrt(upr), fill = 'prediction'), alpha = 0.8, fill="gray") 
q2 = q1 + geom_point(aes(color=position))+ coord_cartesian( ylim=c(-1,8))
q3 = q2 + geom_text(aes(label=paste(substr(last_name,1,3),team)), size=3, vjust=1, 
                    position=position_jitter(1),
                    data=bss.pred[avg.pts>20 | (var.pts/avg.pts < 2 & avg.pts > 6) | 
                                    var.pts/avg.pts > 5.5])#| var.pts>upr | var.pts < lwr] )
q3 + facet_wrap(facets=~position, ncol=2)

q3 + coord_cartesian(ylim=c(1,8))

bss[,slope:=var.pts/avg.pts]
gamma_fit = fitdistr(bss[avg.pts>15,slope], dgamma, start=.(shape=1, rate=1))
q = ggplot(bss[avg.pts>15], aes(x=slope)) + labs(x="V[pts]/E[pts] (dispersion index)", y="frequency") +
  geom_histogram(aes(y=..density..)) + 
  stat_function(fun=dgamma, args=gamma_fit$estimate, color="red") 
q + geom_text(y=0.1, aes(label=paste(substr(last_name,1,3),team, sep="\n")), size=3, vjust=1, 
            data=bss[avg.pts>20])

# teamwork
teams = dt[, list(
  team = unique(team_abbreviation)[1],
  percentage.3pt = sum(three_point_field_goals_made)/sum(three_point_field_goals_attempted),
  avg.pts = sum(points)/82,
  avg.3pta = sum(three_point_field_goals_attempted)/82,
  avg.3ptm = sum(three_point_field_goals_made)/82),
  by=TID]

teams[, high.a:=as.logical(avg.3pta>quantile(avg.3pta, probs=c(0.1,0.9))[2])]
teams[, low.a:=as.logical(avg.3pta<quantile(avg.3pta, probs=c(0.1,0.9))[1])]
teams[, high.m:=as.logical(avg.3ptm>quantile(avg.3ptm, probs=c(0.1,0.9))[2])]
teams[, low.m:=as.logical(avg.3ptm<quantile(avg.3ptm, probs=c(0.1,0.9))[1])]

lm_fit  = lm(avg.3ptm ~ avg.3pta, data = teams)
teams.pred = data.table(teams, predict(lm_fit, level=0.75, interval = 'prediction'))
names(teams.pred)

q = qplot(x=avg.3pta, y=avg.3ptm, data=teams.pred) + 
  geom_text(aes(label=paste0(team, " ", format(percentage.3pt*100,digits=2), "%")), size=3, vjust=-.3,
            data=teams.pred[avg.3ptm<lwr | avg.3ptm > upr | low.a==T | low.m==T | high.a==T | high.a==T])
q + stat_smooth(method="lm", se=F) + 
  geom_ribbon(aes(y=fit, ymin=lwr, ymax=upr), alpha=0.2)

qplot(x=avg.3ptm, y=percentage.3pt, data=teams) + 
  stat_smooth(method="lm") +
  geom_text(aes(label=paste0(team, " ", format(percentage.3pt*100,digits=2), "%")), size=3, vjust=-.3,
    data=teams.pred[avg.3ptm<lwr | avg.3ptm > upr | low.a==T | low.m==T | high.a==T | high.a==T])

qplot(x=percentage.3pt, y=avg.pts, data=teams) + 
  geom_text(aes(label=paste0(team, " ", format(percentage.3pt*100,digits=2), "%")), size=3, vjust=-.3,
            data=teams.pred[avg.pts>130 | avg.pts < 120 | percentage.3pt < 0.33 | percentage.3pt > 0.38]) +
  stat_smooth(method="lm")

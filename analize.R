setwd('//Users/k.yarygin/Projects/xix')
try(dev.off(), silent = T)
rm(list=ls())
gc()

library(data.table)
library(ggplot2)

# Load data -------------------------------------------------------------------

dt_links <- fread('wikilinks.csv', sep = ';',
    col.names = c('main_name_raw', 'main_name', 'link_name', 'n', 'context')
)[
][main_name_raw != 'Александр Николаевич Серов'
]
dt_links[, .(main_name_raw, main_name)][, unique(.SD)]
dt_nodes <- fread('graph_data/nodes.csv', sep = ';')
dt_nodes[
][
    !(full_name %in% dt_links[, main_name_raw]),
    full_name
]


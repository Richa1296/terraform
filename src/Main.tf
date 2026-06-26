resource local_file sample{
 filename = "sample.txt"
  content = "First terraform file"
}

resource random_integer r_int{
 min = 40
 max = 120
}

## returning in a variable

output number {
 value = random_integer.r_int.result
}
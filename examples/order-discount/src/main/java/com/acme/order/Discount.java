package com.acme.order;
public class Discount {
  public double apply(double total) {
    if (total < 0) throw new IllegalArgumentException("ORD-400");
    return total >= 100.0 ? total * 0.9 : total;
  }
}

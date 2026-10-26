package com.example.order;

/** A rejected order. The code is stable and part of the API (for example ORD-400). */
public class OrderException extends RuntimeException {

    private final String code;

    public OrderException(String code, String message) {
        super(code + ": " + message);
        this.code = code;
    }

    public String code() {
        return code;
    }
}

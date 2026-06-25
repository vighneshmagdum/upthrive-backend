package com.vm.upthrive.controller;


import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
    @GetMapping("/api/testing")
    public String test() {
        return "Backend Running succesfully";
    }
}

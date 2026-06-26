package com.vm.upthrive.controller;

import com.vm.upthrive.dto.request.AuthRequest;
import com.vm.upthrive.dto.request.UserRequest;
import com.vm.upthrive.dto.response.AuthResponse;
import com.vm.upthrive.dto.response.UserResponse;
import com.vm.upthrive.security.JwtService;
import com.vm.upthrive.service.interfaces.UserService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private UserService userService;

    @PostMapping("/register")
    public UserResponse register(
            @Valid @RequestBody UserRequest request
    ) {
        return userService.createUser(request);
    }

    @PostMapping("/login")
    public AuthResponse login(@RequestBody AuthRequest request) {

        Authentication authentication =
                authenticationManager.authenticate(
                        new UsernamePasswordAuthenticationToken(
                                request.getEmail(),
                                request.getPassword()
                        )
                );

        if (authentication.isAuthenticated()) {
            return new AuthResponse(
                    jwtService.generateToken(request.getEmail())
            );
        }

        return new AuthResponse("Login Failed");
    }
}
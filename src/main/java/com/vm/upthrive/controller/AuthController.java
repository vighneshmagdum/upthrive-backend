package com.vm.upthrive.controller;


import com.vm.upthrive.dto.request.AuthRequest;
import com.vm.upthrive.dto.response.AuthResponse;
import com.vm.upthrive.security.JwtService;
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

    @GetMapping("/test")
    public String test(){
        return "endpoitn is running sucessfully";
    }

    @PostMapping("/login")
    public AuthResponse login(
            @RequestBody AuthRequest request
            ){
        Authentication authentication = authenticationManager.authenticate(

                        new UsernamePasswordAuthenticationToken(
                                request.getEmail(),
                                request.getPassword()
                        )
                );
                if (authentication.isAuthenticated()) {
                    return new AuthResponse( jwtService.generateToken(
                            request.getEmail()
                    )
                    );
                }

        return new AuthResponse( "login fsiled");

    }

}

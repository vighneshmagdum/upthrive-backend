package com.vm.upthrive.dto.request;


import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class UserRequest {

    @NotBlank(message = "name is required" )
    private String name;

    @Email(message ="Invalid email")
    @NotBlank(message="email required")
    private String email;

    @Size(min =6, message ="password must be atleast of 6 characters")
    private String password;

    private String role;
}

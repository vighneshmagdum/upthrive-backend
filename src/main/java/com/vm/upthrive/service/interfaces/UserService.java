package com.vm.upthrive.service.interfaces;

import com.vm.upthrive.dto.request.UserRequest;
import com.vm.upthrive.dto.response.UserResponse;

import java.util.List;

public interface UserService {
    UserResponse createUser(UserRequest request);

    List<UserResponse> getAllUsers();

    UserResponse getUserById(Long id);

    void deleteUserById(Long id);

    UserResponse updateUser(Long id, UserRequest request);
}

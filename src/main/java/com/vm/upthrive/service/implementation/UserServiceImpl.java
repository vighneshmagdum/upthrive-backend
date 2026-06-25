package com.vm.upthrive.service.implementation;

import com.vm.upthrive.dto.request.UserRequest;
import com.vm.upthrive.dto.response.UserResponse;
import com.vm.upthrive.entity.User;
import com.vm.upthrive.exception.ResourceNotFoundException;
import com.vm.upthrive.repo.UserRepository;
import com.vm.upthrive.service.interfaces.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;
    @Autowired
    private PasswordEncoder passwordEncoder;


    @Override
    public UserResponse createUser(UserRequest request) {

        User user = new User();

        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPassword(
                passwordEncoder.encode(
                        request.getPassword()
                )
        );
        user.setRole(request.getRole());

        User savedUser = userRepository.save(user);
        return new UserResponse(
                savedUser.getId(),
                savedUser.getName(),
                savedUser.getEmail()
        );
    }

    @Override
    public List<UserResponse> getAllUsers() {
        List<User> users = userRepository.findAll();

        return users.stream()
                .map(user -> new UserResponse(
                        user.getId(),
                        user.getName(),
                        user.getEmail()
                ))
                .toList();
    }

    @Override
    public UserResponse getUserById(Long id){
        User user = userRepository.findById(id)
                .orElseThrow(()->new ResourceNotFoundException("User not found"));
        return new UserResponse(
                user.getId(),
                user.getName(),
                user.getEmail()
        );
    }

    @Override
    public void deleteUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(()->new ResourceNotFoundException("User not found"));
        userRepository.delete(user);

    }

    @Override
    public UserResponse updateUser(Long id ,UserRequest request) {
        User user = userRepository.findById(id)
                .orElseThrow(()->new ResourceNotFoundException("User not found"));
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPassword(
                passwordEncoder.encode(
                request.getPassword()
                )
        );
        user.setRole(request.getRole());

        User updatedUser = userRepository.save(user);

        return new UserResponse(
                updatedUser.getId(),
                updatedUser.getName(),
                updatedUser.getEmail()
        );
    }
}
